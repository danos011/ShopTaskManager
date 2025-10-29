import json

from fastapi import APIRouter
from starlette import status

from backend.registry import async_backend_redis
from backend.utils import throw_not_found
from backend.models.status.responses import ResponseStatus

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=ResponseStatus)
async def get_status_by_task_id(task_id: str):
    task_status = await async_backend_redis.get(f"celery-task-meta-{task_id}")

    if task_status is None:
        throw_not_found("Task not found!")

    data_dict = json.loads(task_status)

    return ResponseStatus(status=data_dict["status"])
