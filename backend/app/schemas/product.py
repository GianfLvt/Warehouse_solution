from datetime import datetime

from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    barcode: str | None = None
    name: str
    description: str | None = None
    category: str | None = None
    supplier: str | None = None
    purchase_price: float = 0
    sale_price: float = 0
    quantity: int = 0
    min_stock: int = 0
    max_stock: int = 0
    reorder_point: int = 0
    reorder_quantity: int = 0
    location: str | None = None


class ProductUpdate(BaseModel):
    sku: str | None = None
    barcode: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None
    supplier: str | None = None
    purchase_price: float | None = None
    sale_price: float | None = None
    quantity: int | None = None
    min_stock: int | None = None
    max_stock: int | None = None
    reorder_point: int | None = None
    reorder_quantity: int | None = None
    location: str | None = None
    is_active: bool | None = None


class ProductOut(BaseModel):
    id: int
    sku: str
    barcode: str | None
    name: str
    description: str | None
    category: str | None
    supplier: str | None
    purchase_price: float
    sale_price: float
    quantity: int
    min_stock: int
    max_stock: int
    reorder_point: int
    reorder_quantity: int
    location: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
