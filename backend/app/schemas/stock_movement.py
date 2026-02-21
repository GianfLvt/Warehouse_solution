from datetime import datetime

from pydantic import BaseModel


class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: str
    quantity: int
    notes: str | None = None


class StockMovementOut(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: int
    notes: str | None
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
