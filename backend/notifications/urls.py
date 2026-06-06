from django.urls import path
from .views import send_reminder

urlpatterns = [
    path('recordatorio/', send_reminder, name='send_reminder'),
]
