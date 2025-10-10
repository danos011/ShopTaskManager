from pydantic import BaseModel, EmailStr, Field


class RequestOrder(BaseModel):
    order_id: int = Field(..., title="Order ID")
    product: str = Field(..., title="Product name")
    quantity: int = Field(..., ge=1, title="Quantity")
    email: EmailStr = Field(..., title="Customer email")
