from celery import Celery
from celery.signals import worker_shutdown, worker_ready

from celery_service.config import celery_config
import logging.config

logging.config.fileConfig("backend/logging.conf")

celery_logger = logging.getLogger(__name__)

CELERY = Celery(
    "worker",
    broker=celery_config.celery_broker_dsn,
    backend=celery_config.celery_backend_dsn,
    include=["backend.tasks.worker_tasks", "backend.tasks.beat_tasks"],
    result_expires=3600,
)

CELERY.conf.task_routes = {
    "backend.tasks.worker_tasks.send_notification": {"queue": "priority"},
    "backend.tasks.worker_tasks.process_order": {"queue": "default"},
    "backend.tasks.worker_tasks.generate_invoice": {"queue": "default"},
    "backend.tasks.beat_tasks.daily_stock_report": {"queue": "default"},
    "backend.tasks.beat_tasks.check_pending_orders": {"queue": "default"},
}

CELERY.conf.beat_schedule = {
    "daily_stock_report": {
        "task": "backend.tasks.beat_tasks.daily_stock_report",
        "schedule": 86400.0,
    },
    "check_pending_orders": {
        "task": "backend.tasks.beat_tasks.check_pending_orders",
        "schedule": 300.0,
    },
}

CELERY.conf.update(
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Подключение Redis при запуске воркера"""
    celery_logger.info("Celery worker starting, connecting to Redis...")

    try:
        from backend.registry import broker_redis, backend_redis

        if not broker_redis.client:
            broker_redis.connect()
        if not backend_redis.client:
            backend_redis.connect()

        celery_logger.info("Redis connected for Celery worker")
    except Exception as e:
        celery_logger.error(f"Failed to connect Redis in worker: {e}")


@worker_shutdown.connect
def on_worker_shutdown(**kwargs):
    """Graceful shutdown для Celery"""
    celery_logger.info("Celery worker shutting down, closing Redis connections...")

    try:
        from backend.registry import broker_redis, backend_redis

        broker_redis.close()
        backend_redis.close()
        celery_logger.info("Redis connections closed successfully")
    except Exception as e:
        celery_logger.error(f"Error closing Redis connections: {e}")
