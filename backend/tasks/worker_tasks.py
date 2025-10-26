import time
import logging

from celery_service.celery_app import CELERY
from backend.utils import throw_bad_request, create_invoice
from backend.registry import backend_redis

celery_logger = logging.getLogger(__name__)


@CELERY.task(name="backend.tasks.worker_tasks.process_order", bind=True)
def process_order(self, order_id: int, product: str, quantity: int, email: str):
    try:

        check_status = backend_redis.get(f"order:{order_id}:status")

        celery_logger.info(f"check_status, {check_status}")

        if check_status is not None:
            celery_logger.error(f"This order {order_id} has already been received!")
            raise throw_bad_request("This order has already been received!")

        check_product = backend_redis.get(f"stock:{product}")

        if check_product is not None:
            celery_logger.error(f"This product {order_id} is absent!")
            raise throw_bad_request(f"This product {order_id} is absent!")

        stock_key = f"stock:{product}"
        current_stock = backend_redis.get(stock_key)

        if current_stock is None or int(current_stock) < quantity:
            celery_logger.error(f"{stock_key}: Insufficient stock!")
            raise throw_bad_request(f"{stock_key}: Insufficient stock!")

        new_stock = int(current_stock) - quantity
        backend_redis.set(stock_key, new_stock)
        celery_logger.info("New stock: ", new_stock)
        backend_redis.set(f"order:{order_id}:status", "processed")

        message = f"Your order #{order_id} has been processed successfully!"

        send_notification.delay(email=email, message=message)

        generate_invoice.delay(order_id=order_id, product=product, quantity=quantity)
    except Exception as error:
        celery_logger.error(f"Error in process_order: {error}")
        raise


@CELERY.task(name="backend.tasks.worker_tasks.send_notification")
def send_notification(email: str, message: str):
    try:

        if "@" not in email:
            celery_logger.error(f"Invalid email: {email}")
            raise throw_bad_request("Invalid email")
        time.sleep(5)
        celery_logger.info(f"Sent notification to {email}: {message}")

    except Exception as error:
        celery_logger.error(f"Error in send_notification: {error}")
        raise


@CELERY.task(name="backend.tasks.worker_tasks.generate_invoice")
def generate_invoice(order_id: int, product: str, quantity: int):
    try:
        """Генерация PDF инвойса с помощью FPDF"""
        celery_logger.info(f"Generating PDF invoice for order {order_id}")

        pdf_bytes = create_invoice(order_id, product, quantity)

        if pdf_bytes is None or not len(pdf_bytes):
            celery_logger.warning("Pdf_bytes is empty!")

        backend_redis.set(f"invoice:{order_id}", pdf_bytes)

        celery_logger.info(f"Invoice generated and saved for order {order_id}")

    except Exception as error:
        celery_logger.error(f"Error in generate_invoice: {error}")
        raise
