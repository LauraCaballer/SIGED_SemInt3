from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("prendas", "0003_prenda_archivado"),
    ]

    operations = [
        migrations.AddField(
            model_name="prenda",
            name="demand_calculado_en",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="prenda",
            name="demand_label",
            field=models.CharField(default="Baja", max_length=10),
        ),
        migrations.AddField(
            model_name="prenda",
            name="demand_recomendacion",
            field=models.CharField(default="→ Mantener", max_length=20),
        ),
        migrations.AddField(
            model_name="prenda",
            name="demand_score",
            field=models.FloatField(default=0),
        ),
    ]
