from pydantic import BaseModel, Field, EmailStr


class RequestNotification(BaseModel):
    email: EmailStr = Field(..., title="Customer email")
    message: str = Field(..., title="Message")
