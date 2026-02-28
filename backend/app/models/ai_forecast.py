from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AIForecast(Base):
    __tablename__ = "ai_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    forecast_type: Mapped[str] = mapped_column(String(50), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id"))
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    predicted_value: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    actual_value: Mapped[float | None] = mapped_column(Float)
    model_version: Mapped[str | None] = mapped_column(String(50))
    parameters_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SlottingSuggestion(Base):
    __tablename__ = "slotting_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    current_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    suggested_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    reason: Mapped[str] = mapped_column(String(50))
    priority_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperatorPerformance(Base):
    __tablename__ = "operator_performance"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    period_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    picks_completed: Mapped[int] = mapped_column(Integer, default=0)
    picks_errors: Mapped[int] = mapped_column(Integer, default=0)
    avg_pick_time_sec: Mapped[float] = mapped_column(Float, default=0)
    items_packed: Mapped[int] = mapped_column(Integer, default=0)
    items_received: Mapped[int] = mapped_column(Integer, default=0)
    distance_walked_m: Mapped[float] = mapped_column(Float, default=0)
    efficiency_score: Mapped[float] = mapped_column(Float, default=0)


class AnomalyDetection(Base):
    __tablename__ = "anomaly_detections"

    id: Mapped[int] = mapped_column(primary_key=True)
    anomaly_type: Mapped[str] = mapped_column(String(50), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int | None]
    description: Mapped[str] = mapped_column(Text)
    suggested_action: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
