from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceros", "0003_cliente_archivado_proveedor_archivado"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="ciclo_compra_promedio_dias",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="cliente",
            name="prediccion_calculada_en",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="probabilidad_compra",
            field=models.CharField(default="Baja", max_length=10),
        ),
        migrations.AddField(
            model_name="cliente",
            name="productos_recomendados",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="cliente",
            name="proxima_compra_estimada",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="rfm_frequency",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="cliente",
            name="rfm_monetary_promedio",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="cliente",
            name="rfm_recency_dias",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="cliente",
            name="rfm_score",
            field=models.FloatField(default=0),
        ),
    ]
