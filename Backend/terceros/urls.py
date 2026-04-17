from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProveedorViewSet, ClienteViewSet

# Crear un router que genera automáticamente las rutas CRUD
router = DefaultRouter()
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'clientes', ClienteViewSet, basename='cliente')

urlpatterns = [
    path('', include(router.urls)),
]
