from datetime import datetime

from pydantic import BaseModel


class AddressCreate(BaseModel):
    label: str | None = None
    address: str
    city: str
    zip_code: str
    province: str | None = None
    country: str = "Italia"
    is_default: bool = False


class AddressOut(BaseModel):
    id: int
    label: str | None
    address: str
    city: str
    zip_code: str
    province: str | None
    country: str
    is_default: bool

    model_config = {"from_attributes": True}


class CustomerCreate(BaseModel):
    company_name: str | None = None
    contact_name: str
    email: str | None = None
    phone: str | None = None
    customer_type: str = "B2C"
    notes: str | None = None
    addresses: list[AddressCreate] = []


class CustomerUpdate(BaseModel):
    company_name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    customer_type: str | None = None
    notes: str | None = None


class CustomerOut(BaseModel):
    id: int
    company_name: str | None
    contact_name: str
    email: str | None
    phone: str | None
    customer_type: str
    notes: str | None
    created_at: datetime
    addresses: list[AddressOut] = []

    model_config = {"from_attributes": True}
