from django.urls import path

from .views import (
    ClientePrediccionAPIView,
    EnviarRecomendacionesAPIView,
    EnviarSugerenciasMasivasAPIView,
    ProductoDemandaAPIView,
    RecalcularClientePrediccionAPIView,
    RecalcularDemandasAPIView,
)

urlpatterns = [
    path("clientes/<int:cliente_id>/", ClientePrediccionAPIView.as_view(), name="cliente-prediccion"),
    path("clientes/<int:cliente_id>/recalcular/", RecalcularClientePrediccionAPIView.as_view(), name="cliente-prediccion-recalcular"),
    path("clientes/<int:cliente_id>/enviar/", EnviarRecomendacionesAPIView.as_view(), name="cliente-prediccion-enviar"),
    path("clientes/enviar-masivo/", EnviarSugerenciasMasivasAPIView.as_view(), name="cliente-prediccion-enviar-masivo"),
    path("prendas/<int:producto_id>/", ProductoDemandaAPIView.as_view(), name="producto-demanda"),
    path("prendas/recalcular/", RecalcularDemandasAPIView.as_view(), name="producto-demanda-recalcular"),
]
