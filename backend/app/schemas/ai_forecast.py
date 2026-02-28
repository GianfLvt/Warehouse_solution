from datetime import datetime

from pydantic import BaseModel


class AIForecastOut(BaseModel):
    id: int
    forecast_type: str
    product_id: int | None
    warehouse_id: int | None
    period_start: datetime
    period_end: datetime
    predicted_value: float
    confidence: float
    actual_value: float | None
    model_version: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SlottingSuggestionOut(BaseModel):
    id: int
    product_id: int
    current_location_id: int | None
    suggested_location_id: int
    reason: str
    priority_score: float
    status: str
    applied_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OperatorPerformanceOut(BaseModel):
    id: int
    user_id: int
    period_date: datetime
    picks_completed: int
    picks_errors: int
    avg_pick_time_sec: float
    items_packed: int
    items_received: int
    distance_walked_m: float
    efficiency_score: float

    model_config = {"from_attributes": True}


class AnomalyDetectionOut(BaseModel):
    id: int
    anomaly_type: str
    severity: str
    entity_type: str
    entity_id: int | None
    description: str
    suggested_action: str | None
    status: str
    resolved_at: datetime | None
    resolved_by: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StockPrediction(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    predicted_demand_30d: float
    days_until_stockout: int | None
    reorder_suggested: bool
    suggested_quantity: int


class SeasonalTrend(BaseModel):
    month: int
    avg_demand: float
    predicted_demand: float
    trend: str
