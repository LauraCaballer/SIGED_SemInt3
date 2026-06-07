from django.contrib import admin

from .models import CorreoRecomendacion


@admin.register(CorreoRecomendacion)
class CorreoRecomendacionAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "fecha_envio", "estado")
    list_filter = ("estado", "fecha_envio")
    search_fields = ("cliente__nombre", "cliente__cedula", "cliente__email")
