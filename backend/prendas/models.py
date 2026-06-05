from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

# Create your models here.
class TipoPrenda(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        if not self.nombre or not self.nombre.strip():
            raise ValidationError("El nombre del tipo de prenda no puede estar vacío")
        self.nombre = self.nombre.strip().title()

    class Meta:
        verbose_name = "Tipo de Prenda"
        verbose_name_plural = "Tipos de Prenda"

class TipoOro(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        if not self.nombre or not self.nombre.strip():
            raise ValidationError("El nombre del tipo de oro no puede estar vacío")
        self.nombre = self.nombre.strip().upper()

    class Meta:
        verbose_name = "Tipo de Oro"
        verbose_name_plural = "Tipos de Oro"

class Prenda(models.Model):
    nombre = models.CharField(max_length=100, unique=True, default="Sin nombre")
    tipo_prenda = models.ForeignKey(
        "TipoPrenda", 
        on_delete=models.RESTRICT
    )
    tipo_oro = models.ForeignKey(
        "TipoOro", 
        on_delete=models.RESTRICT
    )
    es_chatarra = models.BooleanField(default=False)
    es_recuperable = models.BooleanField(default=False)
    archivado = models.BooleanField(default=False)
    gramos = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    existencia = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.tipo_prenda.nombre} - {self.tipo_oro.nombre} ({self.gramos}g)"

    def clean(self):
        if self.gramos <= 0:
            raise ValidationError("El peso en gramos debe ser mayor que cero")
        if self.es_chatarra and self.es_recuperable:
            raise ValidationError("Una prenda no puede ser chatarra y recuperable al mismo tiempo")

    def valor_estimado(self, precio_gramo):
        """Calcula el valor estimado de la prenda"""
        return self.gramos * precio_gramo

    def tiene_stock(self, cantidad_requerida=1):
        """Verifica si hay suficiente stock"""
        return self.existencia >= cantidad_requerida

    class Meta:
        verbose_name = "Prenda"
        verbose_name_plural = "Prendas"
        constraints = [
            models.CheckConstraint(
                check=models.Q(gramos__gt=0),
                name='prenda_gramos_positivos'
            ),
            models.CheckConstraint(
                check=models.Q(existencia__gte=0),
                name='prenda_existencia_no_negativa'
            ),
        ]
