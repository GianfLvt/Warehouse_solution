from datetime import datetime

from pydantic import BaseModel


class PickingTaskOut(BaseModel):
    id: int
    wave_id: int
    order_id: int | None
    product_id: int
    source_location_id: int
    lot_id: int | None
    requested_quantity: int
    picked_quantity: int
    status: str
    sequence: int
    picked_at: datetime | None
    picked_by: int | None

    model_config = {"from_attributes": True}


class PickingWaveCreate(BaseModel):
    warehouse_id: int
    wave_type: str = "single"
    priority: int = 5
    assigned_user_id: int | None = None
    zone_id: int | None = None
    order_ids: list[int] = []
    notes: str | None = None


class PickingWaveOut(BaseModel):
    id: int
    wave_number: str
    warehouse_id: int
    wave_type: str
    status: str
    priority: int
    assigned_user_id: int | None
    zone_id: int | None
    started_at: datetime | None
    completed_at: datetime | None
    notes: str | None
    created_by: int
    created_at: datetime
    tasks: list[PickingTaskOut] = []

    model_config = {"from_attributes": True}


class PickConfirm(BaseModel):
    task_id: int
    picked_quantity: int


class PickingWaveListOut(BaseModel):
    id: int
    wave_number: str
    wave_type: str
    status: str
    priority: int
    assigned_user_id: int | None
    task_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
