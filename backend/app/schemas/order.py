from datetime import datetime

from pydantic import BaseModel

from app.schemas.customer import CustomerOut
from app.schemas.product import ProductOut


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product: ProductOut | None = None

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_id: int
    address_id: int | None = None
    notes: str | None = None
    items: list[OrderItemCreate]


class OrderUpdateStatus(BaseModel):
    status: str


class OrderOut(BaseModel):
    id: int
    customer_id: int
    address_id: int | None
    user_id: int
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut] = []
    customer: CustomerOut | None = None

    model_config = {"from_attributes": True}
