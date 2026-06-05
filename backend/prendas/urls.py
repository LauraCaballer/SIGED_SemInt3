from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoPrendaViewSet, TipoOroViewSet, PrendaViewSet

router = DefaultRouter()
router.register(r'tipos-prenda', TipoPrendaViewSet, basename='tipo-prenda')
router.register(r'tipos-oro', TipoOroViewSet, basename='tipo-oro')
router.register(r'prendas', PrendaViewSet, basename='prenda')

urlpatterns = [
    path('', include(router.urls)),
]
