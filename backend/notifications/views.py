import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from terceros.models import Cliente

from .models import ConfiguracionNotificacion, RecordatorioEnvio
from .serializers import ConfiguracionNotificacionSerializer
from .services import enviar_correo_recordatorio, ejecutar_recordatorios_automaticos


@csrf_exempt
@require_POST
def send_reminder(request):
    try:
        data = json.loads(request.body)
        client_email = data.get("client_email")
        client_name = data.get("client_name")
        deuda_monto = data.get("deuda_monto")
        deuda_tipo = data.get("deuda_tipo")
        deuda_venta_id = data.get("deuda_venta_id")
        client_id = data.get("client_id")

        if not client_email or str(client_email).strip() == "" or str(client_email).lower() == "null":
            return JsonResponse({"error": "El cliente no tiene un correo electrónico registrado."}, status=400)

        try:
            canal = enviar_correo_recordatorio(
                client_email,
                client_name,
                deuda_tipo,
                deuda_venta_id,
                deuda_monto,
            )
        except Exception as exc:
            if client_id:
                cliente = Cliente.objects.filter(pk=client_id).first()
                if cliente:
                    RecordatorioEnvio.objects.create(
                        cliente=cliente,
                        deuda_id=int(deuda_venta_id or 0),
                        tipo_deuda="credito" if str(deuda_tipo).lower().startswith("cr") else "apartado",
                        estado="fallido",
                        detalle=str(exc),
                    )
            return JsonResponse({"error": "Failed to send email", "detail": str(exc)}, status=500)

        if client_id:
            cliente = Cliente.objects.filter(pk=client_id).first()
            if cliente:
                RecordatorioEnvio.objects.create(
                    cliente=cliente,
                    deuda_id=int(deuda_venta_id or 0),
                    tipo_deuda="credito" if str(deuda_tipo).lower().startswith("cr") else "apartado",
                    estado="enviado",
                    detalle=f"Enviado por {canal}",
                )

        return JsonResponse({"message": "Email sent successfully", "channel": canal})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class ConfiguracionNotificacionView(APIView):
    def get(self, request):
        config = ConfiguracionNotificacion.load()
        serializer = ConfiguracionNotificacionSerializer(config)
        return Response(serializer.data)

    def put(self, request):
        config = ConfiguracionNotificacion.load()
        serializer = ConfiguracionNotificacionSerializer(config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EjecutarRecordatoriosAutomaticosView(APIView):
    def post(self, request):
        resultado = ejecutar_recordatorios_automaticos()
        return Response(resultado, status=status.HTTP_200_OK)
