from fastapi import APIRouter

from backend.tasks.worker_tasks import generate_invoice

router = APIRouter(prefix="/invoice", tags=["Invoice"])


@router.get("/{order_id}", response_model=str)
async def get_invoice_by_order_id(order_id: int):
    generate_invoice.delay()
    return "str"
