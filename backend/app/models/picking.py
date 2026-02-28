from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PickingWave(Base):
    __tablename__ = "picking_waves"

    id: Mapped[int] = mapped_column(primary_key=True)
    wave_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    wave_type: Mapped[str] = mapped_column(String(20), default="single")
    status: Mapped[str] = mapped_column(String(30), default="creato")
    priority: Mapped[int] = mapped_column(Integer, default=5)
    assigned_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse_zones.id"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tasks: Mapped[list["PickingTask"]] = relationship(back_populates="wave", cascade="all, delete-orphan")
    warehouse: Mapped["Warehouse"] = relationship()
    assigned_user: Mapped["User | None"] = relationship(foreign_keys=[assigned_user_id])


class PickingTask(Base):
    __tablename__ = "picking_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    wave_id: Mapped[int] = mapped_column(ForeignKey("picking_waves.id", ondelete="CASCADE"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    source_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("lots.id"))
    requested_quantity: Mapped[int] = mapped_column(Integer)
    picked_quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    picked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    picked_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    wave: Mapped["PickingWave"] = relationship(back_populates="tasks")
    product: Mapped["Product"] = relationship()
    source_location: Mapped["Location"] = relationship()


from app.models.warehouse import Warehouse, Location  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.user import User  # noqa: E402
