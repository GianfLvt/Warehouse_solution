from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    weight: Mapped[float | None] = mapped_column(Float)
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    carrier: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order: Mapped["Order"] = relationship(back_populates="packages")
    items: Mapped[list["PackageItem"]] = relationship(back_populates="package", cascade="all, delete-orphan")


class PackageItem(Base):
    __tablename__ = "package_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)

    package: Mapped["Package"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


from app.models.order import Order  # noqa: E402
from app.models.product import Product  # noqa: E402
