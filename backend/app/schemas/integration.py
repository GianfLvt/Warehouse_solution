from datetime import datetime

from pydantic import BaseModel


class IntegrationConfigCreate(BaseModel):
    name: str
    integration_type: str
    provider: str
    api_url: str | None = None
    api_key_encrypted: str | None = None
    config_json: str | None = None
    sync_interval_minutes: int = 60


class IntegrationConfigUpdate(BaseModel):
    name: str | None = None
    api_url: str | None = None
    api_key_encrypted: str | None = None
    config_json: str | None = None
    is_active: bool | None = None
    sync_interval_minutes: int | None = None


class IntegrationConfigOut(BaseModel):
    id: int
    name: str
    integration_type: str
    provider: str
    api_url: str | None
    is_active: bool
    last_sync: datetime | None
    sync_interval_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class IntegrationLogOut(BaseModel):
    id: int
    integration_id: int
    direction: str
    entity_type: str
    entity_id: int | None
    status: str
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookEventOut(BaseModel):
    id: int
    event_type: str
    source: str
    status: str
    processed_at: datetime | None
    error_message: str | None
    retry_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
