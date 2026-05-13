from rest_framework import serializers
from .models import Proveedor, Cliente


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

    def validate(self, data):
        """
        Validación personalizada: solo verifica los campos que vienen en la solicitud.
        """
        # Validar nombre si viene en los datos
        if 'nombre' in data:
            if not data['nombre'].strip():
                raise serializers.ValidationError({"nombre": "El nombre del proveedor es obligatorio."})
            data['nombre'] = data['nombre'].strip().title()

        # Validar que haya al menos un contacto (solo si ambos están presentes o ausentes)
        if 'telefono' in data or 'email' in data:
            telefono = data.get('telefono') or getattr(self.instance, 'telefono', None)
            email = data.get('email') or getattr(self.instance, 'email', None)
            if not telefono and not email:
                raise serializers.ValidationError("Debe proporcionar al menos un teléfono o un correo electrónico.")

        return data


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate(self, data):
        """
        Validación personalizada para actualizaciones parciales.
        Solo valida los campos enviados.
        """
        # Validar nombre si viene en los datos
        if 'nombre' in data:
            if not data['nombre'].strip():
                raise serializers.ValidationError({"nombre": "El nombre del cliente es obligatorio."})
            data['nombre'] = data['nombre'].strip().title()

        # Validar cédula si viene en los datos
        if 'cedula' in data:
            if not data['cedula'].strip():
                raise serializers.ValidationError({"cedula": "La cédula del cliente es obligatoria."})
            data['cedula'] = data['cedula'].strip()

        return data
