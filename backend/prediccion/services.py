from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.core.mail import EmailMultiAlternatives
from django.db.models import Avg, Count, Max, Sum
from django.db.models.functions import ExtractMonth
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from compra_venta.models import Venta, VentaPrenda
from prendas.models import Prenda
from terceros.models import Cliente


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def _productos_globales_fallback(excluidos=None, limite=3):
    excluidos = set(excluidos or [])
    qs = (
        VentaPrenda.objects.exclude(prenda_id__in=excluidos)
        .values("prenda_id")
        .annotate(total=Sum("cantidad"))
        .order_by("-total", "prenda_id")
    )

    ids = []
    for row in qs:
        if row["prenda_id"] not in excluidos and Prenda.objects.filter(pk=row["prenda_id"], archivado=False).exists():
            ids.append(row["prenda_id"])
        if len(ids) >= limite:
            break
    return ids


def calcular_rfm(cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    ventas = list(Venta.objects.filter(cliente=cliente).order_by("fecha", "id"))

    hoy = timezone.localdate()

    if not ventas:
        return {
            "rfm_score": 0,
            "rfm_recency_dias": 0,
            "rfm_frequency": 0,
            "rfm_monetary_promedio": Decimal("0.00"),
            "ciclo_compra_promedio_dias": 0,
            "proxima_compra_estimada": None,
            "probabilidad_compra": "Baja",
        }

    ultima_compra = ventas[-1].fecha
    recency_dias = max((hoy - ultima_compra).days, 0)

    ultimos_por_cliente = Venta.objects.values("cliente_id").annotate(ultima=Max("fecha"))
    max_inactividad = 0
    for row in ultimos_por_cliente:
        if row["ultima"]:
            max_inactividad = max(max_inactividad, max((hoy - row["ultima"]).days, 0))
    max_inactividad = max(max_inactividad, 1)
    r = _clamp(1 - (recency_dias / max_inactividad))

    total_compras = len(ventas)
    max_compras = Venta.objects.values("cliente_id").annotate(n=Count("id")).aggregate(max_n=Max("n"))["max_n"] or 1
    f = _clamp(total_compras / max_compras)

    ticket_promedio = Venta.objects.filter(cliente=cliente).aggregate(avg=Avg("total"))["avg"] or Decimal("0.00")
    max_ticket = (
        Venta.objects.values("cliente_id")
        .annotate(avg_t=Avg("total"))
        .aggregate(max_t=Max("avg_t"))["max_t"]
        or Decimal("1.00")
    )
    m = _clamp(float(ticket_promedio) / float(max_ticket or 1))

    score = round((r * 0.40 + f * 0.35 + m * 0.25) * 100, 2)

    fechas = [venta.fecha for venta in ventas]
    if len(fechas) >= 2:
        deltas = [(fechas[i + 1] - fechas[i]).days for i in range(len(fechas) - 1)]
        ciclo = max(int(sum(deltas) / len(deltas)), 1)
    else:
        ciclo = 90

    proxima = ultima_compra + timedelta(days=ciclo)

    if score >= 70:
        probabilidad = "Alta"
    elif score >= 40:
        probabilidad = "Media"
    else:
        probabilidad = "Baja"

    return {
        "rfm_score": score,
        "rfm_recency_dias": recency_dias,
        "rfm_frequency": total_compras,
        "rfm_monetary_promedio": Decimal(str(round(float(ticket_promedio), 2))),
        "ciclo_compra_promedio_dias": ciclo,
        "proxima_compra_estimada": proxima,
        "probabilidad_compra": probabilidad,
    }


def recomendar_productos(cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    historial = list(
        VentaPrenda.objects.filter(venta__cliente=cliente)
        .select_related("prenda", "venta", "prenda__tipo_prenda")
        .order_by("venta__fecha", "id")
    )

    if not historial:
        return _productos_globales_fallback(limite=3)

    productos_activos = set(Prenda.objects.filter(archivado=False).values_list("id", flat=True))
    ya_comprados = set(item.prenda_id for item in historial)
    candidatos = defaultdict(float)

    compras_por_producto = defaultdict(list)
    for item in historial:
        compras_por_producto[item.prenda_id].append(item.venta.fecha)

    hoy = timezone.localdate()

    # Estrategia 1: recompra
    for producto_id, fechas in compras_por_producto.items():
        if producto_id not in productos_activos:
            continue
        fechas = sorted(fechas)
        ultima = fechas[-1]
        if len(fechas) >= 2:
            deltas = [(fechas[i + 1] - fechas[i]).days for i in range(len(fechas) - 1)]
            ciclo = max(int(sum(deltas) / len(deltas)), 1)
        else:
            ciclo = 90
        vence_en = ultima + timedelta(days=ciclo)
        if vence_en <= hoy + timedelta(days=30):
            dias_restantes = max((vence_en - hoy).days, 0)
            candidatos[producto_id] += max(35, 100 - (dias_restantes * 3)) * 1.5

    # Estrategia 2: colaborativo simple
    if Cliente.objects.count() >= 20:
        score = cliente.rfm_score or 0
        clientes_similares = Cliente.objects.filter(
            rfm_score__range=(max(score - 10, 0), min(score + 10, 100))
        ).exclude(pk=cliente.pk)

        if clientes_similares.exists():
            similares = (
                VentaPrenda.objects.filter(venta__cliente__in=clientes_similares)
                .exclude(prenda_id__in=ya_comprados)
                .values("prenda_id")
                .annotate(frecuencia=Sum("cantidad"))
                .order_by("-frecuencia")
            )
            similares = list(similares[:15])
            max_freq = max((row["frecuencia"] or 1 for row in similares), default=1)
            for row in similares:
                producto_id = row["prenda_id"]
                if producto_id in productos_activos:
                    candidatos[producto_id] += ((row["frecuencia"] or 0) / max_freq) * 100 * 1.0

    # Estrategia 3: categoría/tipo favorito
    categoria_favorita = (
        VentaPrenda.objects.filter(venta__cliente=cliente)
        .values("prenda__tipo_prenda_id")
        .annotate(total=Sum("subtotal"))
        .order_by("-total")
        .first()
    )

    if categoria_favorita and categoria_favorita["prenda__tipo_prenda_id"]:
        top_categoria = (
            VentaPrenda.objects.filter(prenda__tipo_prenda_id=categoria_favorita["prenda__tipo_prenda_id"])
            .exclude(prenda_id__in=ya_comprados)
            .values("prenda_id")
            .annotate(frecuencia=Sum("cantidad"))
            .order_by("-frecuencia")
        )
        top_categoria = list(top_categoria[:15])
        max_freq = max((row["frecuencia"] or 1 for row in top_categoria), default=1)
        for row in top_categoria:
            producto_id = row["prenda_id"]
            if producto_id in productos_activos:
                candidatos[producto_id] += ((row["frecuencia"] or 0) / max_freq) * 100 * 0.7

    if not candidatos:
        return _productos_globales_fallback(excluidos=ya_comprados, limite=3)

    factor = max(cliente.rfm_score, 25) / 100
    ranking = sorted(candidatos, key=lambda pid: candidatos[pid] * factor, reverse=True)

    top = []
    vistos = set()
    for producto_id in ranking:
        if producto_id in productos_activos and producto_id not in vistos:
            top.append(producto_id)
            vistos.add(producto_id)
        if len(top) == 3:
            break

    if len(top) < 3:
        for producto_id in _productos_globales_fallback(excluidos=vistos | ya_comprados, limite=3 - len(top)):
            if producto_id not in vistos:
                top.append(producto_id)
                vistos.add(producto_id)
            if len(top) == 3:
                break

    return top[:3]


def calcular_prediccion_cliente(cliente_id):
    rfm = calcular_rfm(cliente_id)
    recomendaciones = recomendar_productos(cliente_id)

    Cliente.objects.filter(pk=cliente_id).update(
        **rfm,
        productos_recomendados=recomendaciones,
        prediccion_calculada_en=timezone.now(),
    )

    return {
        **rfm,
        "productos_recomendados": recomendaciones,
    }


def calcular_demand_score(producto_id):
    producto = Prenda.objects.get(pk=producto_id)
    hoy = timezone.localdate()
    hace_90_dias = hoy - timedelta(days=90)
    mes_actual = hoy.month

    clientes = Cliente.objects.only("rfm_score", "productos_recomendados")
    suma_rfm_activos = 0
    for cliente in clientes:
        if producto_id in (cliente.productos_recomendados or []):
            suma_rfm_activos += float(cliente.rfm_score or 0)

    max_rfm_posible = max(Cliente.objects.count() * 100, 1)
    demanda_activa = min(suma_rfm_activos / max_rfm_posible, 1.0)

    ventas_producto = (
        VentaPrenda.objects.filter(prenda=producto, venta__fecha__gte=hace_90_dias)
        .aggregate(total=Sum("cantidad"))
        .get("total")
        or 0
    )

    max_ventas_categoria = (
        VentaPrenda.objects.filter(prenda__tipo_prenda=producto.tipo_prenda, venta__fecha__gte=hace_90_dias)
        .values("prenda_id")
        .annotate(total=Sum("cantidad"))
        .aggregate(maximo=Max("total"))
        .get("maximo")
        or 1
    )
    ventas_historicas = float(ventas_producto) / float(max_ventas_categoria or 1)

    rfm_compradores = (
        VentaPrenda.objects.filter(prenda=producto)
        .aggregate(avg_rfm=Avg("venta__cliente__rfm_score"))
        .get("avg_rfm")
        or 0
    )
    rfm_compradores_norm = float(rfm_compradores) / 100

    ventas_mes_actual = (
        VentaPrenda.objects.filter(prenda=producto, venta__fecha__month=mes_actual)
        .aggregate(total=Sum("cantidad"))
        .get("total")
        or 0
    )

    ventas_por_mes = (
        VentaPrenda.objects.filter(prenda=producto)
        .annotate(mes=ExtractMonth("venta__fecha"))
        .values("mes")
        .annotate(total=Sum("cantidad"))
    )
    ventas_por_mes = list(ventas_por_mes)
    if ventas_por_mes:
        ventas_promedio_mensual = sum(row["total"] or 0 for row in ventas_por_mes) / len(ventas_por_mes)
    else:
        ventas_promedio_mensual = 1

    estacionalidad = min(float(ventas_mes_actual) / float(ventas_promedio_mensual or 1), 2.0) / 2.0

    score = (
        demanda_activa * 0.40
        + ventas_historicas * 0.30
        + rfm_compradores_norm * 0.20
        + estacionalidad * 0.10
    ) * 100
    score = round(min(score, 100), 2)

    if score >= 70:
        label = "Alta"
    elif score >= 40:
        label = "Media"
    else:
        label = "Baja"

    ventas_90d = float(ventas_producto or 0.1)
    dias_cobertura = (float(producto.existencia or 0) / ventas_90d * 90) if ventas_90d else 999

    if score >= 70 and dias_cobertura < 30:
        recomendacion = "↑ Comprar más"
    elif score >= 40 or dias_cobertura >= 30:
        recomendacion = "→ Mantener"
    else:
        recomendacion = "↓ Reducir"

    return {
        "demand_score": score,
        "demand_label": label,
        "demand_recomendacion": recomendacion,
        "demand_calculado_en": timezone.now(),
    }


def calcular_demand_todos_los_productos():
    for producto in Prenda.objects.filter(archivado=False):
        datos = calcular_demand_score(producto.pk)
        Prenda.objects.filter(pk=producto.pk).update(**datos)


def enviar_recomendaciones_por_correo(cliente):
    producto_ids = cliente.productos_recomendados or []
    if not producto_ids:
        return None

    productos = list(Prenda.objects.filter(pk__in=producto_ids))
    productos.sort(key=lambda producto: producto_ids.index(producto.pk))

    html_content = render_to_string(
        "emails/recomendaciones.html",
        {
            "cliente": cliente,
            "productos": productos,
        },
    )

    msg = EmailMultiAlternatives(
        subject=f"Selección especial para ti, {cliente.nombre}",
        body="Tu joyería tiene productos seleccionados especialmente para ti.",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[cliente.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return [producto.pk for producto in productos]


def enviar_sugerencias_a_clientes_activos():
    from prediccion.models import CorreoRecomendacion

    clientes = (
        Cliente.objects.filter(archivado=False)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
    )

    enviados = 0
    omitidos = 0
    errores = []

    for cliente in clientes:
        try:
            if not cliente.productos_recomendados:
                calcular_prediccion_cliente(cliente.id)
                cliente.refresh_from_db()

            productos_ids = cliente.productos_recomendados or []
            if not productos_ids:
                omitidos += 1
                CorreoRecomendacion.objects.create(
                    cliente=cliente,
                    productos_incluidos=[],
                    estado="omitido",
                )
                continue

            productos = list(Prenda.objects.filter(pk__in=productos_ids))
            productos.sort(key=lambda producto: productos_ids.index(producto.pk))

            html_content = render_to_string(
                "emails/recomendaciones.html",
                {
                    "cliente": cliente,
                    "productos": productos,
                    "intro_text": "Pensamos que esto podría gustarte.",
                },
            )

            msg = EmailMultiAlternatives(
                subject=f"Pensamos que esto podría gustarte, {cliente.nombre}",
                body="Tenemos productos que creemos que podrían gustarte.",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                to=[cliente.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            enviados += 1
            CorreoRecomendacion.objects.create(
                cliente=cliente,
                productos_incluidos=productos_ids,
                estado="enviado",
            )
        except Exception as exc:
            omitidos += 1
            errores.append({"cliente_id": cliente.id, "error": str(exc)})
            CorreoRecomendacion.objects.create(
                cliente=cliente,
                productos_incluidos=cliente.productos_recomendados or [],
                estado="fallido",
            )

    return {
        "enviados": enviados,
        "omitidos": omitidos,
        "errores": errores,
        "procesados": enviados + omitidos,
    }
