from fastapi import APIRouter

router = APIRouter(prefix="/invoice", tags=["Invoice"])


@router.get("/{order_id}", response_model=str)
async def get_order_id(order_id: int):
    return "str"
