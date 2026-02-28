from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(500))
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), default="Italia")
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Rome")
    total_area_sqm: Mapped[float | None] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    zones: Mapped[list["WarehouseZone"]] = relationship(back_populates="warehouse", cascade="all, delete-orphan")
    dock_slots: Mapped[list["DockSlot"]] = relationship(back_populates="warehouse", cascade="all, delete-orphan")


class WarehouseZone(Base):
    __tablename__ = "warehouse_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(255))
    zone_type: Mapped[str] = mapped_column(String(30), default="storage")
    temperature_controlled: Mapped[bool] = mapped_column(Boolean, default=False)
    min_temp: Mapped[float | None] = mapped_column(Float)
    max_temp: Mapped[float | None] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    warehouse: Mapped["Warehouse"] = relationship(back_populates="zones")
    locations: Mapped[list["Location"]] = relationship(back_populates="zone", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("warehouse_id", "code", name="uq_zone_code"),)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("warehouse_zones.id", ondelete="CASCADE"))
    aisle: Mapped[str] = mapped_column(String(10))
    rack: Mapped[str] = mapped_column(String(10))
    level: Mapped[str] = mapped_column(String(10))
    bin: Mapped[str] = mapped_column(String(10))
    barcode: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    location_type: Mapped[str] = mapped_column(String(30), default="shelf")
    max_weight_kg: Mapped[float | None] = mapped_column(Float)
    max_volume_m3: Mapped[float | None] = mapped_column(Float)
    current_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    current_volume_m3: Mapped[float] = mapped_column(Float, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    x_pos: Mapped[int | None] = mapped_column(Integer)
    y_pos: Mapped[int | None] = mapped_column(Integer)

    zone: Mapped["WarehouseZone"] = relationship(back_populates="locations")
    inventory: Mapped[list["LocationInventory"]] = relationship(back_populates="location", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("zone_id", "aisle", "rack", "level", "bin", name="uq_location_position"),)


class LocationInventory(Base):
    __tablename__ = "location_inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("lots.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    location: Mapped["Location"] = relationship(back_populates="inventory")
    product: Mapped["Product"] = relationship()
    lot: Mapped["Lot | None"] = relationship()

    __table_args__ = (UniqueConstraint("location_id", "product_id", "lot_id", name="uq_loc_product_lot"),)


class DockSlot(Base):
    __tablename__ = "dock_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(20))
    dock_type: Mapped[str] = mapped_column(String(20), default="both")
    status: Mapped[str] = mapped_column(String(20), default="free")
    reserved_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reserved_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    warehouse: Mapped["Warehouse"] = relationship(back_populates="dock_slots")


from app.models.product import Product  # noqa: E402
from app.models.lot import Lot  # noqa: E402
