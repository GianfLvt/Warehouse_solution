from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class IoTDevice(Base):
    __tablename__ = "iot_devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    device_type: Mapped[str] = mapped_column(String(30))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("warehouse_zones.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="online")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    firmware_version: Mapped[str | None] = mapped_column(String(50))
    config_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("iot_devices.id", ondelete="CASCADE"), index=True)
    reading_type: Mapped[str] = mapped_column(String(30))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    is_alert: Mapped[bool] = mapped_column(default=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class RFIDScan(Base):
    __tablename__ = "rfid_scans"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[str] = mapped_column(String(100), index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("iot_devices.id"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    event_type: Mapped[str] = mapped_column(String(30))
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
