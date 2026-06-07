from rest_framework import serializers

from .models import CorreoRecomendacion


class CorreoRecomendacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorreoRecomendacion
        fields = "__all__"
