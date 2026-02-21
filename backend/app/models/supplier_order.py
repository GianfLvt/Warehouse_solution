from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SupplierOrder(Base):
    __tablename__ = "supplier_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="inviato")
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    items: Mapped[list["SupplierOrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class SupplierOrderItem(Base):
    __tablename__ = "supplier_order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("supplier_orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float, default=0)

    order: Mapped["SupplierOrder"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


from app.models.product import Product  # noqa: E402
