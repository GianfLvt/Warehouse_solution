from datetime import datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    lot_number: Mapped[str] = mapped_column(String(100), index=True)
    production_date: Mapped[datetime | None] = mapped_column(Date)
    expiry_date: Mapped[datetime | None] = mapped_column(Date)
    supplier_lot: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="active")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship()
    serials: Mapped[list["SerialNumber"]] = relationship(back_populates="lot", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("product_id", "lot_number", name="uq_product_lot"),)


class SerialNumber(Base):
    __tablename__ = "serial_numbers"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("lots.id", ondelete="SET NULL"))
    serial: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="available")
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship()
    lot: Mapped["Lot | None"] = relationship(back_populates="serials")


from app.models.product import Product  # noqa: E402
