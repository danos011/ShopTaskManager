from fastapi import APIRouter
from .invoice import invoice_router
from .order import order_router
from .notification import notification_router


router = APIRouter(prefix="/api")
router.include_router(invoice_router)
router.include_router(notification_router)
router.include_router(order_router)
