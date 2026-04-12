from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import TipoPrenda, TipoOro, Prenda
from .serializers import TipoPrendaSerializer, TipoOroSerializer, PrendaSerializer


class SafeModelViewSet(viewsets.ModelViewSet):
    """
    Clase base para manejar excepciones comunes y permitir actualizaciones parciales.
    """
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({"error": "Ya existe un registro con este nombre."}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al crear el registro: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al actualizar el registro: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        nombre = str(instance)
        instance.delete()
        return Response({"mensaje": f"'{nombre}' eliminado correctamente."}, status=status.HTTP_200_OK)


class TipoPrendaViewSet(SafeModelViewSet):
    queryset = TipoPrenda.objects.all().order_by('nombre')
    serializer_class = TipoPrendaSerializer


class TipoOroViewSet(SafeModelViewSet):
    queryset = TipoOro.objects.all().order_by('nombre')
    serializer_class = TipoOroSerializer


class PrendaViewSet(SafeModelViewSet):
    queryset = Prenda.objects.select_related('tipo_prenda', 'tipo_oro').all().order_by('id')
    serializer_class = PrendaSerializer
