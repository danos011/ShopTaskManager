import uuid

from pydantic import BaseModel


class ResponseOrder(BaseModel):
    task_id: uuid.UUID
