from fastapi import APIRouter

from backend.models.order.requests import RequestOrder
from backend.models.order.responses import ResponseOrder
from backend.registry import db_redis

router = APIRouter(prefix="/order", tags=["Order"])


@router.post("/", response_model=ResponseOrder)
async def order(data: RequestOrder) -> ResponseOrder:
    return ResponseOrder(task_id=1)
