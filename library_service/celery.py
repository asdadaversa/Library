import os

from celery.schedules import crontab

from library_service import settings
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
app = Celery("library_service", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

app.config_from_object("django.conf:settings")

app.autodiscover_tasks(packages=["borrowings.periodic_tasks", "payments.periodic_tasks"])


app.conf.beat_schedule = {
    "send overdue  borrowings notifications": {
        "task": "borrowings.periodic_tasks.send_overdue_borrowing_notification",
        "schedule": crontab(hour="18", minute="18"),
    },
    "check stripe session for expiration": {
        "task": "payments.periodic_tasks.check_session_for_expiration",
        "schedule": crontab(minute="*"),
    }
}

app.conf.update(
    CELERY_FLOWER={
         "broker": "redis://127.0.0.1:6379/1",
    }
)
