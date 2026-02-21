from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str | None] = mapped_column(String(255))
    contact_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    customer_type: Mapped[str] = mapped_column(String(10), default="B2C")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    addresses: Mapped[list["CustomerAddress"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    label: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    zip_code: Mapped[str] = mapped_column(String(20))
    province: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(100), default="Italia")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    customer: Mapped["Customer"] = relationship(back_populates="addresses")
