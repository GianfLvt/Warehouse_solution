from datetime import datetime

from pydantic import BaseModel


class PackageItemCreate(BaseModel):
    product_id: int
    quantity: int


class PackageItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    model_config = {"from_attributes": True}


class PackageCreate(BaseModel):
    order_id: int
    weight: float | None = None
    tracking_number: str | None = None
    carrier: str | None = None
    items: list[PackageItemCreate] = []


class PackageUpdate(BaseModel):
    weight: float | None = None
    tracking_number: str | None = None
    carrier: str | None = None


class PackageOut(BaseModel):
    id: int
    order_id: int
    weight: float | None
    tracking_number: str | None
    carrier: str | None
    created_at: datetime
    items: list[PackageItemOut] = []

    model_config = {"from_attributes": True}
