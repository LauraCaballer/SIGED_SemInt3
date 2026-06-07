from django.contrib import admin

from .models import ConfiguracionNotificacion, RecordatorioEnvio


@admin.register(ConfiguracionNotificacion)
class ConfiguracionNotificacionAdmin(admin.ModelAdmin):
    list_display = ("id", "activo", "frecuencia")


@admin.register(RecordatorioEnvio)
class RecordatorioEnvioAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "tipo_deuda", "deuda_id", "estado", "fecha_envio")
    list_filter = ("tipo_deuda", "estado", "fecha_envio")
    search_fields = ("cliente__nombre", "cliente__cedula", "cliente__email", "deuda_id")
