from datetime import datetime

from pydantic import BaseModel


class IoTDeviceCreate(BaseModel):
    device_code: str
    device_type: str
    warehouse_id: int
    zone_id: int | None = None
    location_id: int | None = None
    name: str
    firmware_version: str | None = None
    config_json: str | None = None


class IoTDeviceUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    zone_id: int | None = None
    location_id: int | None = None
    firmware_version: str | None = None
    config_json: str | None = None


class IoTDeviceOut(BaseModel):
    id: int
    device_code: str
    device_type: str
    warehouse_id: int
    zone_id: int | None
    location_id: int | None
    name: str
    status: str
    last_seen: datetime | None
    firmware_version: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SensorReadingCreate(BaseModel):
    device_id: int
    reading_type: str
    value: float
    unit: str
    is_alert: bool = False


class SensorReadingOut(BaseModel):
    id: int
    device_id: int
    reading_type: str
    value: float
    unit: str
    is_alert: bool
    recorded_at: datetime

    model_config = {"from_attributes": True}


class RFIDScanCreate(BaseModel):
    tag_id: str
    device_id: int
    product_id: int | None = None
    location_id: int | None = None
    event_type: str


class RFIDScanOut(BaseModel):
    id: int
    tag_id: str
    device_id: int
    product_id: int | None
    location_id: int | None
    event_type: str
    scanned_at: datetime

    model_config = {"from_attributes": True}
