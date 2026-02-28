from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CycleCount(Base):
    __tablename__ = "cycle_counts"

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse_zones.id"))
    count_type: Mapped[str] = mapped_column(String(30), default="full")
    status: Mapped[str] = mapped_column(String(20), default="pianificato")
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assigned_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    total_locations: Mapped[int] = mapped_column(Integer, default=0)
    counted_locations: Mapped[int] = mapped_column(Integer, default=0)
    discrepancies: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CycleCountItem(Base):
    __tablename__ = "cycle_count_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle_count_id: Mapped[int] = mapped_column(ForeignKey("cycle_counts.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("lots.id"))
    system_quantity: Mapped[int] = mapped_column(Integer)
    counted_quantity: Mapped[int | None] = mapped_column(Integer)
    variance: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    counted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    counted_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_type: Mapped[str] = mapped_column(String(30))
    reference_id: Mapped[int] = mapped_column(Integer)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("lots.id"))
    check_type: Mapped[str] = mapped_column(String(30))
    result: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    checked_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
