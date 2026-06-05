from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .models import MetodoPago, Estado
from .serializers import MetodoPagoSerializer, EstadoSerializer

class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({"error": "Ya existe un método de pago con ese nombre."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al crear método de pago: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al actualizar método de pago: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({"error": "Ya existe un estado con ese nombre."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al crear estado: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al actualizar estado: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)