from django.urls import path
from .views import (
    ConfiguracionNotificacionView,
    EjecutarRecordatoriosAutomaticosView,
    send_reminder,
)

urlpatterns = [
    path('recordatorio/', send_reminder, name='send_reminder'),
    path('config/', ConfiguracionNotificacionView.as_view(), name='config_notificaciones'),
    path('recordatorios/ejecutar/', EjecutarRecordatoriosAutomaticosView.as_view(), name='recordatorios_ejecutar'),
]
