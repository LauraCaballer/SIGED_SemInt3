from django.urls import path
from .views import send_reminder

urlpatterns = [
    path('send_reminder/', send_reminder, name='send_reminder'),
]
