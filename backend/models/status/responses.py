from pydantic import BaseModel


class ResponseStatus(BaseModel):
    status: str
