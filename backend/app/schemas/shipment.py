from datetime import datetime

from pydantic import BaseModel


class ShipmentCreate(BaseModel):
    order_id: int | None = None
    warehouse_id: int
    carrier: str
    service_type: str | None = None
    recipient_name: str | None = None
    recipient_address: str | None = None
    dock_slot_id: int | None = None
    notes: str | None = None


class ShipmentUpdate(BaseModel):
    tracking_number: str | None = None
    status: str | None = None
    shipping_cost: float | None = None
    estimated_delivery: datetime | None = None
    notes: str | None = None


class ShipmentOut(BaseModel):
    id: int
    shipment_number: str
    order_id: int | None
    warehouse_id: int
    dock_slot_id: int | None
    carrier: str
    service_type: str | None
    tracking_number: str | None
    status: str
    total_weight_kg: float
    total_volume_m3: float
    total_packages: int
    shipping_cost: float
    estimated_delivery: datetime | None
    shipped_at: datetime | None
    delivered_at: datetime | None
    recipient_name: str | None
    recipient_address: str | None
    notes: str | None
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TruckLoadItemCreate(BaseModel):
    shipment_id: int | None = None
    package_id: int | None = None
    weight_kg: float = 0
    volume_m3: float = 0


class TruckLoadItemOut(BaseModel):
    id: int
    truck_load_id: int
    shipment_id: int | None
    package_id: int | None
    weight_kg: float
    volume_m3: float
    load_sequence: int

    model_config = {"from_attributes": True}


class TruckLoadCreate(BaseModel):
    warehouse_id: int
    dock_slot_id: int | None = None
    truck_plate: str | None = None
    driver_name: str | None = None
    carrier: str | None = None
    max_weight_kg: float = 0
    max_volume_m3: float = 0
    departure_time: datetime | None = None
    notes: str | None = None
    items: list[TruckLoadItemCreate] = []


class TruckLoadUpdate(BaseModel):
    status: str | None = None
    truck_plate: str | None = None
    driver_name: str | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    transport_cost: float | None = None
    notes: str | None = None


class TruckLoadOut(BaseModel):
    id: int
    load_number: str
    warehouse_id: int
    dock_slot_id: int | None
    truck_plate: str | None
    driver_name: str | None
    carrier: str | None
    status: str
    max_weight_kg: float
    max_volume_m3: float
    loaded_weight_kg: float
    loaded_volume_m3: float
    departure_time: datetime | None
    arrival_time: datetime | None
    gps_latitude: float | None
    gps_longitude: float | None
    transport_cost: float
    notes: str | None
    user_id: int
    created_at: datetime
    items: list[TruckLoadItemOut] = []

    model_config = {"from_attributes": True}
