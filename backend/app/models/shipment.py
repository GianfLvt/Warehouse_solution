from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    shipment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    dock_slot_id: Mapped[int | None] = mapped_column(ForeignKey("dock_slots.id"))
    carrier: Mapped[str] = mapped_column(String(255))
    service_type: Mapped[str | None] = mapped_column(String(50))
    tracking_number: Mapped[str | None] = mapped_column(String(200), index=True)
    status: Mapped[str] = mapped_column(String(30), default="preparazione")
    total_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    total_volume_m3: Mapped[float] = mapped_column(Float, default=0)
    total_packages: Mapped[int] = mapped_column(Integer, default=0)
    shipping_cost: Mapped[float] = mapped_column(Float, default=0)
    estimated_delivery: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    recipient_name: Mapped[str | None] = mapped_column(String(255))
    recipient_address: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order: Mapped["Order | None"] = relationship()
    warehouse: Mapped["Warehouse"] = relationship()
    user: Mapped["User"] = relationship()


class TruckLoad(Base):
    __tablename__ = "truck_loads"

    id: Mapped[int] = mapped_column(primary_key=True)
    load_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    dock_slot_id: Mapped[int | None] = mapped_column(ForeignKey("dock_slots.id"))
    truck_plate: Mapped[str | None] = mapped_column(String(20))
    driver_name: Mapped[str | None] = mapped_column(String(255))
    carrier: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="pianificato")
    max_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    max_volume_m3: Mapped[float] = mapped_column(Float, default=0)
    loaded_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    loaded_volume_m3: Mapped[float] = mapped_column(Float, default=0)
    departure_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arrival_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    gps_latitude: Mapped[float | None] = mapped_column(Float)
    gps_longitude: Mapped[float | None] = mapped_column(Float)
    transport_cost: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    items: Mapped[list["TruckLoadItem"]] = relationship(back_populates="truck_load", cascade="all, delete-orphan")
    warehouse: Mapped["Warehouse"] = relationship()


class TruckLoadItem(Base):
    __tablename__ = "truck_load_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    truck_load_id: Mapped[int] = mapped_column(ForeignKey("truck_loads.id", ondelete="CASCADE"))
    shipment_id: Mapped[int | None] = mapped_column(ForeignKey("shipments.id"))
    package_id: Mapped[int | None] = mapped_column(ForeignKey("packages.id"))
    weight_kg: Mapped[float] = mapped_column(Float, default=0)
    volume_m3: Mapped[float] = mapped_column(Float, default=0)
    load_sequence: Mapped[int] = mapped_column(Integer, default=0)

    truck_load: Mapped["TruckLoad"] = relationship(back_populates="items")


from app.models.order import Order  # noqa: E402
from app.models.warehouse import Warehouse  # noqa: E402
from app.models.user import User  # noqa: E402
