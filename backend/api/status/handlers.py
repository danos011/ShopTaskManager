import json

from fastapi import APIRouter
from starlette import status

from backend.registry import backend_redis
from backend.utils import throw_not_found
from backend.models.status.responses import ResponseStatus

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=ResponseStatus)
async def get_status_by_task_id(task_id: str):
    task_status = backend_redis.get(f"celery-task-meta-{task_id}")

    if not len(task_status):
        throw_not_found("Status not found!")

    data_dict = json.loads(task_status)

    return ResponseStatus(status=data_dict["status"])
