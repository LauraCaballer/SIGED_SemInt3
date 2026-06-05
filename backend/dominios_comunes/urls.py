from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetodoPagoViewSet, EstadoViewSet

router = DefaultRouter()
router.register(r'metodos-pago', MetodoPagoViewSet, basename='metodo-pago')
router.register(r'estados', EstadoViewSet, basename='estado')

urlpatterns = [
    path('', include(router.urls)),
]