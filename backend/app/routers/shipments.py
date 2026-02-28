import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.shipment import Shipment, TruckLoad, TruckLoadItem
from app.models.user import User
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentOut,
    ShipmentUpdate,
    TruckLoadCreate,
    TruckLoadOut,
    TruckLoadUpdate,
)

router = APIRouter(prefix="/api/shipments", tags=["shipments"])

SHIPMENT_STATUSES = ["preparazione", "pronto", "spedito", "in_transito", "consegnato", "annullato"]
TRUCK_STATUSES = ["pianificato", "in_carico", "in_transito", "consegnato", "annullato"]


def generate_shipment_number() -> str:
    return f"SHP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def generate_load_number() -> str:
    return f"TRK-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@router.get("", response_model=list[ShipmentOut])
def list_shipments(
    status: str | None = None,
    warehouse_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Shipment)
    if status:
        q = q.filter(Shipment.status == status)
    if warehouse_id:
        q = q.filter(Shipment.warehouse_id == warehouse_id)
    return q.order_by(Shipment.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=ShipmentOut, status_code=201)
def create_shipment(data: ShipmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    shipment = Shipment(
        shipment_number=generate_shipment_number(),
        user_id=current_user.id,
        **data.model_dump(),
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.get("/{shipment_id}", response_model=ShipmentOut)
def get_shipment(shipment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    s = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Spedizione non trovata")
    return s


@router.put("/{shipment_id}", response_model=ShipmentOut)
def update_shipment(shipment_id: int, data: ShipmentUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    s = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Spedizione non trovata")
    updates = data.model_dump(exclude_unset=True)
    if "status" in updates:
        if updates["status"] not in SHIPMENT_STATUSES:
            raise HTTPException(status_code=400, detail=f"Stato non valido. Valori: {', '.join(SHIPMENT_STATUSES)}")
        if updates["status"] == "spedito" and not s.shipped_at:
            s.shipped_at = datetime.now(timezone.utc)
        if updates["status"] == "consegnato" and not s.delivered_at:
            s.delivered_at = datetime.now(timezone.utc)
    for field, value in updates.items():
        setattr(s, field, value)
    db.commit()
    db.refresh(s)
    return s


@router.get("/tracking/{tracking_number}", response_model=ShipmentOut)
def track_shipment(tracking_number: str, db: Session = Depends(get_db)):
    s = db.query(Shipment).filter(Shipment.tracking_number == tracking_number).first()
    if not s:
        raise HTTPException(status_code=404, detail="Spedizione non trovata")
    return s


@router.get("/trucks", response_model=list[TruckLoadOut])
def list_trucks(
    status: str | None = None,
    warehouse_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(TruckLoad).options(joinedload(TruckLoad.items))
    if status:
        q = q.filter(TruckLoad.status == status)
    if warehouse_id:
        q = q.filter(TruckLoad.warehouse_id == warehouse_id)
    return q.order_by(TruckLoad.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/trucks", response_model=TruckLoadOut, status_code=201)
def create_truck(data: TruckLoadCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    truck = TruckLoad(
        load_number=generate_load_number(),
        warehouse_id=data.warehouse_id,
        dock_slot_id=data.dock_slot_id,
        truck_plate=data.truck_plate,
        driver_name=data.driver_name,
        carrier=data.carrier,
        max_weight_kg=data.max_weight_kg,
        max_volume_m3=data.max_volume_m3,
        departure_time=data.departure_time,
        notes=data.notes,
        user_id=current_user.id,
    )
    db.add(truck)
    db.flush()
    total_w = 0.0
    total_v = 0.0
    for idx, item_data in enumerate(data.items):
        item = TruckLoadItem(truck_load_id=truck.id, load_sequence=idx + 1, **item_data.model_dump())
        db.add(item)
        total_w += item_data.weight_kg
        total_v += item_data.volume_m3
    truck.loaded_weight_kg = total_w
    truck.loaded_volume_m3 = total_v
    db.commit()
    return db.query(TruckLoad).options(joinedload(TruckLoad.items)).filter(TruckLoad.id == truck.id).first()


@router.get("/trucks/{truck_id}", response_model=TruckLoadOut)
def get_truck(truck_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    t = db.query(TruckLoad).options(joinedload(TruckLoad.items)).filter(TruckLoad.id == truck_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Carico camion non trovato")
    return t


@router.put("/trucks/{truck_id}", response_model=TruckLoadOut)
def update_truck(truck_id: int, data: TruckLoadUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    t = db.query(TruckLoad).filter(TruckLoad.id == truck_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Carico camion non trovato")
    updates = data.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] not in TRUCK_STATUSES:
        raise HTTPException(status_code=400, detail=f"Stato non valido. Valori: {', '.join(TRUCK_STATUSES)}")
    for field, value in updates.items():
        setattr(t, field, value)
    db.commit()
    db.refresh(t)
    return db.query(TruckLoad).options(joinedload(TruckLoad.items)).filter(TruckLoad.id == truck_id).first()
