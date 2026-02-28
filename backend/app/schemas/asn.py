from datetime import datetime

from pydantic import BaseModel


class ASNItemCreate(BaseModel):
    product_id: int
    expected_quantity: int
    lot_number: str | None = None
    target_location_id: int | None = None
    unit_price: float = 0


class ASNItemOut(BaseModel):
    id: int
    product_id: int
    expected_quantity: int
    received_quantity: int
    lot_number: str | None
    target_location_id: int | None
    unit_price: float
    status: str

    model_config = {"from_attributes": True}


class ASNCreate(BaseModel):
    supplier: str
    warehouse_id: int
    dock_slot_id: int | None = None
    expected_date: datetime | None = None
    carrier: str | None = None
    tracking_number: str | None = None
    notes: str | None = None
    items: list[ASNItemCreate]


class ASNUpdateStatus(BaseModel):
    status: str


class ASNReceiveItem(BaseModel):
    asn_item_id: int
    received_quantity: int
    lot_number: str | None = None
    location_id: int | None = None


class ASNOut(BaseModel):
    id: int
    asn_number: str
    supplier: str
    warehouse_id: int
    dock_slot_id: int | None
    status: str
    expected_date: datetime | None
    arrived_at: datetime | None
    completed_at: datetime | None
    carrier: str | None
    tracking_number: str | None
    notes: str | None
    user_id: int
    created_at: datetime
    items: list[ASNItemOut] = []

    model_config = {"from_attributes": True}
