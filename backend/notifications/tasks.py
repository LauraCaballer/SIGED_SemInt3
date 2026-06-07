try:
    from celery import shared_task
except Exception:  # pragma: no cover
    def shared_task(func=None, **kwargs):
        if func is None:
            def decorator(inner):
                return inner

            return decorator
        return func


@shared_task
def ejecutar_recordatorios_automaticos_task():
    from .services import ejecutar_recordatorios_automaticos

    return ejecutar_recordatorios_automaticos()
