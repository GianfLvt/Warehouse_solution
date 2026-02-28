from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    barcode: Mapped[str | None] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    subcategory: Mapped[str | None] = mapped_column(String(100))
    supplier: Mapped[str | None] = mapped_column(String(255))
    purchase_price: Mapped[float] = mapped_column(Float, default=0)
    sale_price: Mapped[float] = mapped_column(Float, default=0)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    max_stock: Mapped[int] = mapped_column(Integer, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, default=0)
    reorder_quantity: Mapped[int] = mapped_column(Integer, default=0)
    location_aisle: Mapped[str | None] = mapped_column(String(20))
    location_shelf: Mapped[str | None] = mapped_column(String(20))
    location_level: Mapped[str | None] = mapped_column(String(20))
    location_bin: Mapped[str | None] = mapped_column(String(20))
    default_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id"))
    weight_kg: Mapped[float] = mapped_column(Float, default=0)
    width_cm: Mapped[float] = mapped_column(Float, default=0)
    height_cm: Mapped[float] = mapped_column(Float, default=0)
    depth_cm: Mapped[float] = mapped_column(Float, default=0)
    volume_m3: Mapped[float] = mapped_column(Float, default=0)
    lot_tracking: Mapped[bool] = mapped_column(Boolean, default=False)
    serial_tracking: Mapped[bool] = mapped_column(Boolean, default=False)
    expiry_tracking: Mapped[bool] = mapped_column(Boolean, default=False)
    storage_strategy: Mapped[str] = mapped_column(String(10), default="FIFO")
    abc_class: Mapped[str | None] = mapped_column(String(1))
    rotation_class: Mapped[str | None] = mapped_column(String(20))
    customs_code: Mapped[str | None] = mapped_column(String(20))
    country_of_origin: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
