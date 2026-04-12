from rest_framework import serializers
from .models import TipoPrenda, TipoOro, Prenda
from django.core.exceptions import ValidationError


class TipoPrendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPrenda
        fields = '__all__'

    def validate_nombre(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre del tipo de prenda no puede estar vacío.")
        return value.strip().title()


class TipoOroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoOro
        fields = '__all__'

    def validate_nombre(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre del tipo de oro no puede estar vacío.")
        return value.strip().upper()


class PrendaSerializer(serializers.ModelSerializer):
    tipo_prenda_nombre = serializers.CharField(source='tipo_prenda.nombre', read_only=True)
    tipo_oro_nombre = serializers.CharField(source='tipo_oro.nombre', read_only=True)

    class Meta:
        model = Prenda
        fields = [
            'id', 'nombre', 'tipo_prenda', 'tipo_prenda_nombre', 
            'tipo_oro', 'tipo_oro_nombre', 
            'es_chatarra', 'es_recuperable', 
            'gramos', 'existencia', 'archivado'
        ]

    def validate(self, data):
        gramos = data.get('gramos', getattr(self.instance, 'gramos', None))
        es_chatarra = data.get('es_chatarra', getattr(self.instance, 'es_chatarra', False))
        es_recuperable = data.get('es_recuperable', getattr(self.instance, 'es_recuperable', False))

        if gramos is not None and gramos <= 0:
            raise serializers.ValidationError({"gramos": "El peso en gramos debe ser mayor que cero."})
        if es_chatarra and es_recuperable:
            raise serializers.ValidationError("Una prenda no puede ser chatarra y recuperable al mismo tiempo.")
        return data
