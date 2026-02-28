from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.integration import IntegrationConfig, IntegrationLog, WebhookEvent
from app.models.user import User
from app.schemas.integration import (
    IntegrationConfigCreate,
    IntegrationConfigOut,
    IntegrationConfigUpdate,
    IntegrationLogOut,
    WebhookEventOut,
)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationConfigOut])
def list_integrations(
    integration_type: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    q = db.query(IntegrationConfig)
    if integration_type:
        q = q.filter(IntegrationConfig.integration_type == integration_type)
    return q.order_by(IntegrationConfig.name).all()


@router.post("", response_model=IntegrationConfigOut, status_code=201)
def create_integration(data: IntegrationConfigCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    if db.query(IntegrationConfig).filter(IntegrationConfig.name == data.name).first():
        raise HTTPException(status_code=400, detail="Nome integrazione già esistente")
    config = IntegrationConfig(**data.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/{integration_id}", response_model=IntegrationConfigOut)
def get_integration(integration_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    c = db.query(IntegrationConfig).filter(IntegrationConfig.id == integration_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Integrazione non trovata")
    return c


@router.put("/{integration_id}", response_model=IntegrationConfigOut)
def update_integration(integration_id: int, data: IntegrationConfigUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    c = db.query(IntegrationConfig).filter(IntegrationConfig.id == integration_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Integrazione non trovata")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{integration_id}", status_code=204)
def delete_integration(integration_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    c = db.query(IntegrationConfig).filter(IntegrationConfig.id == integration_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Integrazione non trovata")
    db.delete(c)
    db.commit()


@router.get("/{integration_id}/logs", response_model=list[IntegrationLogOut])
def list_logs(
    integration_id: int,
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    q = db.query(IntegrationLog).filter(IntegrationLog.integration_id == integration_id)
    if status:
        q = q.filter(IntegrationLog.status == status)
    return q.order_by(IntegrationLog.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/webhooks/events", response_model=list[WebhookEventOut])
def list_webhook_events(
    event_type: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    q = db.query(WebhookEvent)
    if event_type:
        q = q.filter(WebhookEvent.event_type == event_type)
    if status:
        q = q.filter(WebhookEvent.status == status)
    return q.order_by(WebhookEvent.created_at.desc()).offset(skip).limit(limit).all()
