from datetime import datetime

from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    barcode: str | None = None
    name: str
    description: str | None = None
    category: str | None = None
    subcategory: str | None = None
    supplier: str | None = None
    purchase_price: float = 0
    sale_price: float = 0
    quantity: int = 0
    min_stock: int = 0
    max_stock: int = 0
    reorder_point: int = 0
    reorder_quantity: int = 0
    location_aisle: str | None = None
    location_shelf: str | None = None
    location_level: str | None = None
    location_bin: str | None = None
    default_location_id: int | None = None
    warehouse_id: int | None = None
    weight_kg: float = 0
    width_cm: float = 0
    height_cm: float = 0
    depth_cm: float = 0
    volume_m3: float = 0
    lot_tracking: bool = False
    serial_tracking: bool = False
    expiry_tracking: bool = False
    storage_strategy: str = "FIFO"
    abc_class: str | None = None
    rotation_class: str | None = None
    customs_code: str | None = None
    country_of_origin: str | None = None


class ProductUpdate(BaseModel):
    sku: str | None = None
    barcode: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None
    subcategory: str | None = None
    supplier: str | None = None
    purchase_price: float | None = None
    sale_price: float | None = None
    quantity: int | None = None
    min_stock: int | None = None
    max_stock: int | None = None
    reorder_point: int | None = None
    reorder_quantity: int | None = None
    location_aisle: str | None = None
    location_shelf: str | None = None
    location_level: str | None = None
    location_bin: str | None = None
    default_location_id: int | None = None
    warehouse_id: int | None = None
    weight_kg: float | None = None
    width_cm: float | None = None
    height_cm: float | None = None
    depth_cm: float | None = None
    volume_m3: float | None = None
    lot_tracking: bool | None = None
    serial_tracking: bool | None = None
    expiry_tracking: bool | None = None
    storage_strategy: str | None = None
    abc_class: str | None = None
    rotation_class: str | None = None
    customs_code: str | None = None
    country_of_origin: str | None = None
    is_active: bool | None = None


class ProductOut(BaseModel):
    id: int
    sku: str
    barcode: str | None
    name: str
    description: str | None
    category: str | None
    subcategory: str | None
    supplier: str | None
    purchase_price: float
    sale_price: float
    quantity: int
    min_stock: int
    max_stock: int
    reorder_point: int
    reorder_quantity: int
    location_aisle: str | None
    location_shelf: str | None
    location_level: str | None
    location_bin: str | None
    default_location_id: int | None
    warehouse_id: int | None
    weight_kg: float
    width_cm: float
    height_cm: float
    depth_cm: float
    volume_m3: float
    lot_tracking: bool
    serial_tracking: bool
    expiry_tracking: bool
    storage_strategy: str
    abc_class: str | None
    rotation_class: str | None
    customs_code: str | None
    country_of_origin: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
