from fastapi import APIRouter
from starlette import status

from backend.models.notification.requests import RequestNotification
from backend.tasks.worker_tasks import send_notification
from backend.utils import get_ok_message

router = APIRouter(prefix="/notification", tags=["Notification"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=str)
async def test_notification(data: RequestNotification) -> str:
    send_notification.delay(email=data.email, message=data.message)
    return get_ok_message()
