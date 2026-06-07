import os

try:
    from celery import Celery
except Exception:  # pragma: no cover
    Celery = None


if Celery is not None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siged.settings")
    app = Celery("siged")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
