import os
from datetime import timedelta

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from apartado_credito.models import Apartado, Credito, ESTADO_CANCELADO, ESTADO_FINALIZADO
from compra_venta.models import Compra, Venta

from .models import ConfiguracionNotificacion, RecordatorioEnvio


def _frecuencia_a_dias(frecuencia):
    return {"diario": 1, "semanal": 7, "mensual": 30}.get(frecuencia, 7)


def _detalle_deuda(tipo_deuda, deuda):
    if tipo_deuda == "credito":
        venta = Venta.objects.filter(credito=deuda).select_related("cliente").first()
        if not venta:
            return None
        return {
            "cliente": venta.cliente,
            "deuda_id": deuda.id,
            "tipo_deuda": "credito",
            "deuda_tipo_label": "Crédito",
            "venta_id": venta.id,
            "monto_pendiente": deuda.monto_pendiente,
        }

    if tipo_deuda == "apartado":
        venta = Venta.objects.filter(apartado=deuda).select_related("cliente").first()
        if not venta:
            return None
        return {
            "cliente": venta.cliente,
            "deuda_id": deuda.id,
            "tipo_deuda": "apartado",
            "deuda_tipo_label": "Apartado",
            "venta_id": venta.id,
            "monto_pendiente": deuda.monto_pendiente,
        }

    return None


def obtener_deudas_vencidas():
    deudas = []

    ventas = (
        Venta.objects.select_related(
            "cliente",
            "credito",
            "credito__estado",
            "apartado",
            "apartado__estado",
        )
        .filter(Q(credito__isnull=False) | Q(apartado__isnull=False))
        .order_by("id")
    )

    hoy = timezone.localdate()
    estados_bloqueados = {ESTADO_FINALIZADO, ESTADO_CANCELADO}

    for venta in ventas:
        if venta.credito and venta.credito.monto_pendiente > 0:
            credito = venta.credito
            if credito.estado_id not in estados_bloqueados and credito.fecha_limite < hoy:
                detalle = _detalle_deuda("credito", credito)
                if detalle:
                    detalle["deuda"] = credito
                    deudas.append(detalle)
                continue

        if venta.apartado and venta.apartado.monto_pendiente > 0:
            apartado = venta.apartado
            if apartado.estado_id not in estados_bloqueados and apartado.fecha_limite < hoy:
                detalle = _detalle_deuda("apartado", apartado)
                if detalle:
                    detalle["deuda"] = apartado
                    deudas.append(detalle)

    return deudas


def _puede_enviarse(cliente_id, tipo_deuda, deuda_id, frecuencia):
    dias = _frecuencia_a_dias(frecuencia)
    corte = timezone.now() - timedelta(days=dias)
    return not RecordatorioEnvio.objects.filter(
        cliente_id=cliente_id,
        tipo_deuda=tipo_deuda,
        deuda_id=deuda_id,
        estado="enviado",
        fecha_envio__gte=corte,
    ).exists()


def enviar_correo_recordatorio(cliente_email, cliente_nombre, deuda_tipo, deuda_venta_id, deuda_monto):
    html_content = render_to_string(
        "emails/recordatorio_deuda.html",
        {
            "client_name": cliente_nombre or "Cliente",
            "deuda_tipo": deuda_tipo,
            "deuda_venta_id": deuda_venta_id,
            "deuda_monto": deuda_monto,
        },
    )

    api_key = os.getenv("BREVO_API_KEY") or getattr(settings, "BREVO_API_KEY", None)
    sender_email = os.getenv("BREVO_SENDER_EMAIL", getattr(settings, "BREVO_SENDER_EMAIL", "formcreatorufps@gmail.com"))
    sender_name = os.getenv("BREVO_SENDER_NAME", getattr(settings, "BREVO_SENDER_NAME", "SIGED"))

    if api_key:
        payload = {
            "sender": {"email": sender_email, "name": sender_name},
            "to": [{"email": cliente_email, "name": cliente_nombre or ""}],
            "subject": f"SIGED - Recordatorio de pago pendiente (#{deuda_venta_id})",
            "htmlContent": html_content,
        }
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={"api-key": api_key, "Content-Type": "application/json"},
            timeout=30,
        )
        if response.status_code < 200 or response.status_code >= 300:
            raise RuntimeError(f"Brevo respondió {response.status_code}: {response.text}")
        return "brevo"

    msg = EmailMultiAlternatives(
        subject=f"SIGED - Recordatorio de pago pendiente (#{deuda_venta_id})",
        body="Tiene una deuda pendiente registrada en SIGED.",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[cliente_email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return "django-mail"


def ejecutar_recordatorios_automaticos():
    config = ConfiguracionNotificacion.load()
    if not config.activo:
        return {
            "estado": "inactivo",
            "enviados": 0,
            "omitidos": 0,
            "procesados": 0,
            "motivo": "La configuracion de notificaciones esta desactivada",
        }

    deudas = obtener_deudas_vencidas()
    enviados = 0
    omitidos = 0
    procesados = 0
    detalles = []

    for item in deudas:
        procesados += 1
        cliente = item["cliente"]
        deuda = item["deuda"]
        tipo_deuda = item["tipo_deuda"]
        venta_id = item["venta_id"]
        monto_pendiente = item["monto_pendiente"]

        if not cliente.email:
            omitidos += 1
            RecordatorioEnvio.objects.create(
                cliente=cliente,
                deuda_id=deuda.id,
                tipo_deuda=tipo_deuda,
                estado="omitido",
                detalle="Cliente sin correo",
            )
            detalles.append({"cliente": cliente.id, "deuda_id": deuda.id, "estado": "omitido", "motivo": "sin correo"})
            continue

        if not _puede_enviarse(cliente.id, tipo_deuda, deuda.id, config.frecuencia):
            omitidos += 1
            RecordatorioEnvio.objects.create(
                cliente=cliente,
                deuda_id=deuda.id,
                tipo_deuda=tipo_deuda,
                estado="omitido",
                detalle=f"Ya enviado dentro de la frecuencia {config.frecuencia}",
            )
            detalles.append({"cliente": cliente.id, "deuda_id": deuda.id, "estado": "omitido", "motivo": "throttle"})
            continue

        try:
            canal = enviar_correo_recordatorio(
                cliente.email,
                cliente.nombre,
                "Crédito" if tipo_deuda == "credito" else "Apartado",
                venta_id,
                monto_pendiente,
            )
            enviados += 1
            RecordatorioEnvio.objects.create(
                cliente=cliente,
                deuda_id=deuda.id,
                tipo_deuda=tipo_deuda,
                estado="enviado",
                detalle=f"Enviado por {canal}",
            )
            detalles.append({"cliente": cliente.id, "deuda_id": deuda.id, "estado": "enviado", "canal": canal})
        except Exception as exc:
            omitidos += 1
            RecordatorioEnvio.objects.create(
                cliente=cliente,
                deuda_id=deuda.id,
                tipo_deuda=tipo_deuda,
                estado="fallido",
                detalle=str(exc),
            )
            detalles.append({"cliente": cliente.id, "deuda_id": deuda.id, "estado": "fallido", "error": str(exc)})

    return {
        "estado": "ok",
        "enviados": enviados,
        "omitidos": omitidos,
        "procesados": procesados,
        "detalles": detalles,
    }
