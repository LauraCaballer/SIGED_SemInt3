from django.db import models


class ConfiguracionNotificacion(models.Model):
    activo = models.BooleanField(default=False)
    frecuencia = models.CharField(
        max_length=20,
        choices=[("diario", "Diario"), ("semanal", "Semanal"), ("mensual", "Mensual")],
        default="semanal",
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Configuración de Notificación"
        verbose_name_plural = "Configuraciones de Notificación"


class RecordatorioEnvio(models.Model):
    TIPO_DEUDA_CHOICES = [
        ("credito", "Crédito"),
        ("apartado", "Apartado"),
    ]

    ESTADO_CHOICES = [
        ("enviado", "Enviado"),
        ("fallido", "Fallido"),
        ("omitido", "Omitido"),
    ]

    cliente = models.ForeignKey(
        "terceros.Cliente",
        on_delete=models.CASCADE,
        related_name="recordatorios_enviados",
    )
    deuda_id = models.PositiveIntegerField()
    tipo_deuda = models.CharField(max_length=20, choices=TIPO_DEUDA_CHOICES)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="enviado")
    detalle = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-fecha_envio"]
        indexes = [
            models.Index(fields=["cliente", "tipo_deuda", "deuda_id"]),
            models.Index(fields=["fecha_envio"]),
        ]

    def __str__(self):
        return f"Recordatorio {self.tipo_deuda} #{self.deuda_id} - {self.cliente_id} - {self.estado}"
