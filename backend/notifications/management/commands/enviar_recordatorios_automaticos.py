from django.core.management.base import BaseCommand

from notifications.services import ejecutar_recordatorios_automaticos


class Command(BaseCommand):
    help = "Envía recordatorios automáticos de deudas vencidas según la configuración activa"

    def handle(self, *args, **kwargs):
        resultado = ejecutar_recordatorios_automaticos()
        if resultado.get("estado") == "inactivo":
            self.stdout.write(
                self.style.WARNING(
                    resultado.get("motivo", "La configuracion de notificaciones esta desactivada")
                )
            )
            return

        if resultado.get("procesados", 0) == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No se encontraron deudas vencidas con saldo pendiente para enviar recordatorios."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Recordatorios ejecutados: {resultado.get('procesados', 0)} | "
                f"enviados: {resultado.get('enviados', 0)} | "
                f"omitidos: {resultado.get('omitidos', 0)}"
            )
        )
