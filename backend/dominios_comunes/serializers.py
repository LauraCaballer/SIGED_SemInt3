from rest_framework import serializers
from .models import MetodoPago, Estado
from django.core.exceptions import ValidationError

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'

    def validate_nombre(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre del método de pago no puede estar vacío.")
        return value.strip().title()

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'

    def validate_nombre(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre del estado no puede estar vacío.")
        return value.strip().title()