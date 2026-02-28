from datetime import datetime

from pydantic import BaseModel


class LocationBase(BaseModel):
    aisle: str
    rack: str
    level: str
    bin: str
    barcode: str
    location_type: str = "shelf"
    max_weight_kg: float | None = None
    max_volume_m3: float | None = None
    x_pos: int | None = None
    y_pos: int | None = None


class LocationCreate(LocationBase):
    zone_id: int


class LocationOut(LocationBase):
    id: int
    zone_id: int
    current_weight_kg: float
    current_volume_m3: float
    is_active: bool
    is_blocked: bool

    model_config = {"from_attributes": True}


class LocationInventoryOut(BaseModel):
    id: int
    location_id: int
    product_id: int
    lot_id: int | None
    quantity: int
    reserved_quantity: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class WarehouseZoneCreate(BaseModel):
    code: str
    name: str
    zone_type: str = "storage"
    temperature_controlled: bool = False
    min_temp: float | None = None
    max_temp: float | None = None


class WarehouseZoneOut(BaseModel):
    id: int
    warehouse_id: int
    code: str
    name: str
    zone_type: str
    temperature_controlled: bool
    min_temp: float | None
    max_temp: float | None
    is_active: bool
    locations: list[LocationOut] = []

    model_config = {"from_attributes": True}


class DockSlotCreate(BaseModel):
    code: str
    dock_type: str = "both"
    notes: str | None = None


class DockSlotOut(BaseModel):
    id: int
    warehouse_id: int
    code: str
    dock_type: str
    status: str
    reserved_from: datetime | None
    reserved_until: datetime | None
    notes: str | None

    model_config = {"from_attributes": True}


class WarehouseCreate(BaseModel):
    code: str
    name: str
    address: str | None = None
    city: str | None = None
    country: str = "Italia"
    timezone: str = "Europe/Rome"
    total_area_sqm: float | None = None


class WarehouseUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    total_area_sqm: float | None = None
    is_active: bool | None = None


class WarehouseOut(BaseModel):
    id: int
    code: str
    name: str
    address: str | None
    city: str | None
    country: str
    timezone: str
    total_area_sqm: float | None
    is_active: bool
    created_at: datetime
    zones: list[WarehouseZoneOut] = []
    dock_slots: list[DockSlotOut] = []

    model_config = {"from_attributes": True}


class WarehouseListOut(BaseModel):
    id: int
    code: str
    name: str
    city: str | None
    country: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
