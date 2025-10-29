from io import BytesIO

from fastapi import APIRouter
from starlette import status
from starlette.responses import StreamingResponse

from backend.registry import async_backend_redis
from backend.utils import throw_not_found

router = APIRouter(prefix="/invoice", tags=["Invoice"])


@router.get("/{order_id}", status_code=status.HTTP_200_OK, response_model=bytes)
async def get_invoice_by_order_id(order_id: int):
    file = await async_backend_redis.get(f"invoice:{order_id}")

    if not len(file):
        throw_not_found("File not found!")

    return StreamingResponse(
        BytesIO(file),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{order_id}.pdf"},
    )
