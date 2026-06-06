from django.urls import path
from .views import send_reminder, ConfiguracionNotificacionView

urlpatterns = [
    path('recordatorio/', send_reminder, name='send_reminder'),
    path('config/', ConfiguracionNotificacionView.as_view(), name='config_notificaciones'),
]
