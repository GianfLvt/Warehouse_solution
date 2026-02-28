from datetime import datetime

from pydantic import BaseModel


class CycleCountCreate(BaseModel):
    warehouse_id: int
    zone_id: int | None = None
    count_type: str = "full"
    scheduled_date: datetime | None = None
    assigned_user_id: int | None = None
    notes: str | None = None


class CycleCountItemOut(BaseModel):
    id: int
    cycle_count_id: int
    location_id: int
    product_id: int
    lot_id: int | None
    system_quantity: int
    counted_quantity: int | None
    variance: int | None
    status: str
    counted_at: datetime | None
    counted_by: int | None

    model_config = {"from_attributes": True}


class CycleCountOut(BaseModel):
    id: int
    warehouse_id: int
    zone_id: int | None
    count_type: str
    status: str
    scheduled_date: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    assigned_user_id: int | None
    total_locations: int
    counted_locations: int
    discrepancies: int
    notes: str | None
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CountItemSubmit(BaseModel):
    count_item_id: int
    counted_quantity: int


class QualityCheckCreate(BaseModel):
    reference_type: str
    reference_id: int
    product_id: int
    lot_id: int | None = None
    check_type: str
    result: str = "pending"
    notes: str | None = None
    photo_url: str | None = None


class QualityCheckOut(BaseModel):
    id: int
    reference_type: str
    reference_id: int
    product_id: int
    lot_id: int | None
    check_type: str
    result: str
    notes: str | None
    photo_url: str | None
    checked_by: int
    checked_at: datetime

    model_config = {"from_attributes": True}
