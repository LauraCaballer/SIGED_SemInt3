from rest_framework import serializers
from .models import ConfiguracionNotificacion

class ConfiguracionNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionNotificacion
        fields = ['activo', 'frecuencia']
