from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecordatorioEnvio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("deuda_id", models.PositiveIntegerField()),
                ("tipo_deuda", models.CharField(choices=[("credito", "Crédito"), ("apartado", "Apartado")], max_length=20)),
                ("fecha_envio", models.DateTimeField(auto_now_add=True)),
                ("estado", models.CharField(choices=[("enviado", "Enviado"), ("fallido", "Fallido"), ("omitido", "Omitido")], default="enviado", max_length=20)),
                ("detalle", models.TextField(blank=True, null=True)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recordatorios_enviados", to="terceros.cliente")),
            ],
            options={
                "ordering": ["-fecha_envio"],
            },
        ),
        migrations.AddIndex(
            model_name="recordatorioenvio",
            index=models.Index(fields=["cliente", "tipo_deuda", "deuda_id"], name="notifications_cliente__1eb3e7_idx"),
        ),
        migrations.AddIndex(
            model_name="recordatorioenvio",
            index=models.Index(fields=["fecha_envio"], name="notifications_fech_env_1df503_idx"),
        ),
    ]
