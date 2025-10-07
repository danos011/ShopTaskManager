from celery import Celery

from celery_service.config import celery_config

CELERY = Celery(
    __name__,
    broker=celery_config.celery_broker_dsn,
    backend=celery_config.celery_backend_dsn,
    broker_connection_retry_on_startup=True,
    include=["tasks.smtp.tasks", "tasks.sms.tasks"],
)
