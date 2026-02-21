from datetime import datetime

from pydantic import BaseModel

from app.schemas.customer import CustomerOut
from app.schemas.product import ProductOut


class QuoteItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class QuoteItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product: ProductOut | None = None

    model_config = {"from_attributes": True}


class QuoteCreate(BaseModel):
    customer_id: int
    notes: str | None = None
    valid_until: datetime | None = None
    items: list[QuoteItemCreate]


class QuoteUpdateStatus(BaseModel):
    status: str


class QuoteOut(BaseModel):
    id: int
    customer_id: int
    user_id: int
    status: str
    notes: str | None
    valid_until: datetime | None
    created_at: datetime
    items: list[QuoteItemOut] = []
    customer: CustomerOut | None = None

    model_config = {"from_attributes": True}
