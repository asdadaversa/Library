import os

from library_service import settings
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
app = Celery("library_service", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

app.config_from_object("django.conf:settings")

app.autodiscover_tasks(["borrowings", "library_telegram_bot", "library_service"])
