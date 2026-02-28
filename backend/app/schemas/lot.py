from datetime import date, datetime

from pydantic import BaseModel


class LotCreate(BaseModel):
    product_id: int
    lot_number: str
    production_date: date | None = None
    expiry_date: date | None = None
    supplier_lot: str | None = None
    notes: str | None = None


class LotOut(BaseModel):
    id: int
    product_id: int
    lot_number: str
    production_date: date | None
    expiry_date: date | None
    supplier_lot: str | None
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SerialNumberCreate(BaseModel):
    product_id: int
    lot_id: int | None = None
    serial: str
    location_id: int | None = None


class SerialNumberOut(BaseModel):
    id: int
    product_id: int
    lot_id: int | None
    serial: str
    status: str
    location_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
