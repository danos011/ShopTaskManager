from fastapi import APIRouter

from backend.models.order.requests import RequestOrder
from backend.models.order.responses import ResponseOrder
from backend.tasks.worker_tasks import process_order

router = APIRouter(prefix="/order", tags=["Order"])


@router.post("/", response_model=ResponseOrder)
async def order(data: RequestOrder) -> ResponseOrder:
    task = process_order.delay(
        order_id=data.order_id,
        product=data.product,
        quantity=data.quantity,
        email=data.email,
    )

    return ResponseOrder(task_id=1)
