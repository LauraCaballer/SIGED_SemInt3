try:
    from celery import shared_task
except Exception:  # pragma: no cover - fallback cuando Celery no está instalado
    def shared_task(func=None, **kwargs):
        if func is None:
            def decorator(inner):
                return inner

            return decorator
        return func

from datetime import timedelta

from django.utils import timezone


@shared_task
def tarea_calcular_prediccion_cliente(cliente_id):
    from .services import calcular_prediccion_cliente

    return calcular_prediccion_cliente(cliente_id)


@shared_task
def recalcular_predicciones_vencidas():
    from terceros.models import Cliente
    from .services import calcular_prediccion_cliente

    hace_7_dias = timezone.now() - timedelta(days=7)
    clientes = Cliente.objects.filter(prediccion_calculada_en__lt=hace_7_dias).values_list("id", flat=True)

    for cliente_id in clientes:
        calcular_prediccion_cliente(cliente_id)


@shared_task
def recalcular_demand_scores():
    from .services import calcular_demand_todos_los_productos

    return calcular_demand_todos_los_productos()
