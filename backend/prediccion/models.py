from django.db import models


class CorreoRecomendacion(models.Model):
    cliente = models.ForeignKey("terceros.Cliente", on_delete=models.CASCADE, related_name="correos_enviados")
    fecha_envio = models.DateTimeField(auto_now_add=True)
    productos_incluidos = models.JSONField(default=list)
    estado = models.CharField(max_length=20, default="enviado")

    class Meta:
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"Correo recomendación #{self.pk} - {self.cliente_id}"
