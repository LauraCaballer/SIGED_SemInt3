from django.db import migrations, models
from django.db.models.deletion import CASCADE


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("terceros", "0003_cliente_archivado_proveedor_archivado"),
    ]

    operations = [
        migrations.CreateModel(
            name="CorreoRecomendacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_envio", models.DateTimeField(auto_now_add=True)),
                ("productos_incluidos", models.JSONField(default=list)),
                ("estado", models.CharField(default="enviado", max_length=20)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=CASCADE,
                        related_name="correos_enviados",
                        to="terceros.cliente",
                    ),
                ),
            ],
            options={
                "ordering": ["-fecha_envio"],
            },
        ),
    ]
