from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "job_application_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.jobs"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-due-follow-up-reminders": {
            "task": "app.workers.jobs.check_due_reminders",
            "schedule": 300.0,
        }
    },
)
