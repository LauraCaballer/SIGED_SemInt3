from django.db import models

class ConfiguracionNotificacion(models.Model):
    activo = models.BooleanField(default=False)
    frecuencia = models.CharField(
        max_length=20,
        choices=[('diario', 'Diario'), ('semanal', 'Semanal'), ('mensual', 'Mensual')],
        default='semanal'
    )
    
    # We only want one instance of this config, so we can use a singleton pattern or just limit rows
    def save(self, *args, **kwargs):
        self.pk = 1
        super(ConfiguracionNotificacion, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Configuración de Notificación"
        verbose_name_plural = "Configuraciones de Notificación"
