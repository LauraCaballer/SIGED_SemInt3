from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
# Create your models here.
class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True)
    archivado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    def clean(self):
        if not self.nombre or not self.nombre.strip():
            raise ValidationError("El nombre del proveedor es obligatorio")
        self.nombre = self.nombre.strip().title()

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

class Cliente(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cedula = models.CharField(max_length=20, unique=True)
    fecha_registro = models.DateField(auto_now_add=True)
    archivado = models.BooleanField(default=False)
    rfm_score = models.FloatField(default=0)
    rfm_recency_dias = models.IntegerField(default=0)
    rfm_frequency = models.IntegerField(default=0)
    rfm_monetary_promedio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ciclo_compra_promedio_dias = models.IntegerField(default=0)
    proxima_compra_estimada = models.DateField(null=True, blank=True)
    probabilidad_compra = models.CharField(max_length=10, default='Baja')
    productos_recomendados = models.JSONField(default=list)
    prediccion_calculada_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.cedula}"

    def clean(self):
        if not self.nombre or not self.nombre.strip():
            raise ValidationError("El nombre del cliente es obligatorio")
        if not self.cedula or not self.cedula.strip():
            raise ValidationError("La cédula del cliente es obligatoria")
        
        self.nombre = self.nombre.strip().title()
        self.cedula = self.cedula.strip()

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
