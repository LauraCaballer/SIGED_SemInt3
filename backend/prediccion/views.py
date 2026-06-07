from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from prendas.models import Prenda
from prendas.serializers import PrendaSerializer
from terceros.models import Cliente
from terceros.serializers import ClienteSerializer

from .models import CorreoRecomendacion
from .services import (
    calcular_demand_score,
    calcular_demand_todos_los_productos,
    calcular_prediccion_cliente,
    enviar_recomendaciones_por_correo,
)


class ClientePrediccionAPIView(APIView):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, pk=cliente_id)

        if not cliente.prediccion_calculada_en or cliente.prediccion_calculada_en < timezone.now() - timedelta(days=7):
            calcular_prediccion_cliente(cliente.id)
            cliente.refresh_from_db()

        productos_ids = cliente.productos_recomendados or []
        productos = list(Prenda.objects.filter(pk__in=productos_ids))
        productos.sort(key=lambda producto: productos_ids.index(producto.pk))

        data = ClienteSerializer(cliente).data
        data["productos_recomendados_detalle"] = PrendaSerializer(productos, many=True).data
        return Response(data)


class RecalcularClientePrediccionAPIView(APIView):
    def post(self, request, cliente_id):
        calcular_prediccion_cliente(cliente_id)
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        data = ClienteSerializer(cliente).data
        return Response(data, status=status.HTTP_200_OK)


class EnviarRecomendacionesAPIView(APIView):
    def post(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, pk=cliente_id)

        if not cliente.email:
            return Response({"detail": "El cliente no tiene correo registrado."}, status=status.HTTP_400_BAD_REQUEST)

        productos_ids = cliente.productos_recomendados or []
        if not productos_ids:
            calcular_prediccion_cliente(cliente.id)
            cliente.refresh_from_db()
            productos_ids = cliente.productos_recomendados or []

        if not productos_ids:
            return Response({"detail": "No hay recomendaciones disponibles para este cliente."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            enviados = enviar_recomendaciones_por_correo(cliente)
            CorreoRecomendacion.objects.create(
                cliente=cliente,
                productos_incluidos=enviados or productos_ids,
                estado="enviado",
            )
            return Response({"detail": "Correo enviado correctamente."}, status=status.HTTP_200_OK)
        except Exception as exc:
            CorreoRecomendacion.objects.create(
                cliente=cliente,
                productos_incluidos=productos_ids,
                estado="fallido",
            )
            return Response({"detail": f"No se pudo enviar el correo: {exc}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductoDemandaAPIView(APIView):
    def get(self, request, producto_id):
        producto = get_object_or_404(Prenda, pk=producto_id)

        if not producto.demand_calculado_en or producto.demand_calculado_en < timezone.now() - timedelta(days=1):
            datos = calcular_demand_score(producto.id)
            Prenda.objects.filter(pk=producto.id).update(**datos)
            producto.refresh_from_db()

        return Response(PrendaSerializer(producto).data)


class RecalcularDemandasAPIView(APIView):
    def post(self, request):
        calcular_demand_todos_los_productos()
        return Response({"detail": "Demandas recalculadas correctamente."}, status=status.HTTP_200_OK)
