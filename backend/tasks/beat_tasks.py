import logging

from celery_service.celery_app import CELERY
from backend.registry import broker_redis

celery_logger = logging.getLogger(__name__)


@CELERY.task(name="backend.tasks.beat_tasks.daily_stock_report")
def daily_stock_report():
    # Агрегируем остатки и логируем
    keys = broker_redis.keys("stock:*")
    report = {}
    for key in keys:
        report[key] = broker_redis.get(key)
    celery_logger.info(f"Daily stock report: {report}")


@CELERY.task(name="backend.tasks.beat_tasks.check_pending_orders")
def check_pending_orders():
    # Проверка просроченных заказов и повторная постановка в очередь
    keys = broker_redis.keys("order:*:status")
    for key in keys:
        status = broker_redis.get(key)
        if status == b"pending":
            order_id = key.decode().split(":")[1]
            # Повторно поставить задачу в очередь process_order
            broker_redis.delay(order_id)
            celery_logger.info(f"Requeued order {order_id}")
