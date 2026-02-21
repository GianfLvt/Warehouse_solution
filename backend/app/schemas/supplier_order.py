from datetime import datetime

from pydantic import BaseModel

from app.schemas.product import ProductOut


class SupplierOrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float = 0


class SupplierOrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product: ProductOut | None = None

    model_config = {"from_attributes": True}


class SupplierOrderCreate(BaseModel):
    supplier: str
    notes: str | None = None
    items: list[SupplierOrderItemCreate]


class SupplierOrderUpdateStatus(BaseModel):
    status: str


class SupplierOrderOut(BaseModel):
    id: int
    supplier: str
    status: str
    notes: str | None
    user_id: int
    created_at: datetime
    items: list[SupplierOrderItemOut] = []

    model_config = {"from_attributes": True}
