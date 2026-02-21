from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(30), default="bozza")
    notes: Mapped[str | None] = mapped_column(Text)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    items: Mapped[list["QuoteItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    customer: Mapped["Customer"] = relationship()


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)

    quote: Mapped["Quote"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


from app.models.customer import Customer  # noqa: E402
from app.models.product import Product  # noqa: E402
