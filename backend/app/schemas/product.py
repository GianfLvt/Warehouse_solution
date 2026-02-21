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
    location_aisle: str | None = None
    location_shelf: str | None = None
    location_level: str | None = None
    location_bin: str | None = None


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
    location_aisle: str | None = None
    location_shelf: str | None = None
    location_level: str | None = None
    location_bin: str | None = None


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
    location_aisle: str | None
    location_shelf: str | None
    location_level: str | None
    location_bin: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
