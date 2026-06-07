from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from compra_venta.models import VentaPrenda


@receiver(post_save, sender=VentaPrenda)
@receiver(post_delete, sender=VentaPrenda)
def ventas_cambiaron(sender, instance, **kwargs):
    from .tasks import recalcular_demand_scores, tarea_calcular_prediccion_cliente

    cliente_id = instance.venta.cliente_id
    try:
        tarea_calcular_prediccion_cliente.delay(cliente_id)
    except Exception:
        tarea_calcular_prediccion_cliente(cliente_id)

    try:
        recalcular_demand_scores.delay()
    except Exception:
        recalcular_demand_scores()
