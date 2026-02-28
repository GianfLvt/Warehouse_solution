from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ASN(Base):
    __tablename__ = "asns"

    id: Mapped[int] = mapped_column(primary_key=True)
    asn_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    supplier: Mapped[str] = mapped_column(String(255))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    dock_slot_id: Mapped[int | None] = mapped_column(ForeignKey("dock_slots.id"))
    status: Mapped[str] = mapped_column(String(30), default="atteso")
    expected_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    carrier: Mapped[str | None] = mapped_column(String(255))
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    items: Mapped[list["ASNItem"]] = relationship(back_populates="asn", cascade="all, delete-orphan")
    warehouse: Mapped["Warehouse"] = relationship()
    user: Mapped["User"] = relationship()


class ASNItem(Base):
    __tablename__ = "asn_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    asn_id: Mapped[int] = mapped_column(ForeignKey("asns.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    expected_quantity: Mapped[int] = mapped_column(Integer)
    received_quantity: Mapped[int] = mapped_column(Integer, default=0)
    lot_number: Mapped[str | None] = mapped_column(String(100))
    target_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="atteso")

    asn: Mapped["ASN"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


from app.models.warehouse import Warehouse  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.user import User  # noqa: E402
