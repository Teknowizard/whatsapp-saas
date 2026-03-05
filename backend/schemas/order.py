from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from models.order import OrderStatus


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    product_id: int
    amount: Optional[float] = None

    @field_validator("customer_phone")
    @classmethod
    def phone_format(cls, v):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError("Invalid phone number")
        return v


class OrderResponse(BaseModel):
    id: int
    user_id: int
    customer_name: str
    customer_phone: str
    product_id: Optional[int]
    amount: float
    payment_link: Optional[str]
    payment_reference: Optional[str]
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
