from django.apps import AppConfig


class PrediccionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "prediccion"

    def ready(self):
        from . import signals  # noqa: F401
