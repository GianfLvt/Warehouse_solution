import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.order import Order, OrderItem
from app.models.picking import PickingTask, PickingWave
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Location, LocationInventory
from app.schemas.picking import PickConfirm, PickingWaveCreate, PickingWaveListOut, PickingWaveOut

router = APIRouter(prefix="/api/picking", tags=["picking"])

VALID_STATUSES = ["creato", "in_corso", "completato", "annullato"]


def generate_wave_number() -> str:
    return f"WAVE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@router.get("", response_model=list[PickingWaveListOut])
def list_waves(
    status: str | None = None,
    warehouse_id: int | None = None,
    assigned_user_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(
        PickingWave,
        func.count(PickingTask.id).label("task_count"),
    ).outerjoin(PickingTask).group_by(PickingWave.id)

    if status:
        q = q.filter(PickingWave.status == status)
    if warehouse_id:
        q = q.filter(PickingWave.warehouse_id == warehouse_id)
    if assigned_user_id:
        q = q.filter(PickingWave.assigned_user_id == assigned_user_id)

    results = q.order_by(PickingWave.priority.desc(), PickingWave.created_at.desc()).offset(skip).limit(limit).all()
    out = []
    for wave, task_count in results:
        item = PickingWaveListOut.model_validate(wave)
        item.task_count = task_count
        out.append(item)
    return out


@router.post("", response_model=PickingWaveOut, status_code=201)
def create_wave(
    data: PickingWaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "responsabile", "magazziniere")),
):
    wave = PickingWave(
        wave_number=generate_wave_number(),
        warehouse_id=data.warehouse_id,
        wave_type=data.wave_type,
        priority=data.priority,
        assigned_user_id=data.assigned_user_id,
        zone_id=data.zone_id,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(wave)
    db.flush()

    sequence = 0
    for order_id in data.order_ids:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            continue
        items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        for item in items:
            inv = (
                db.query(LocationInventory)
                .filter(LocationInventory.product_id == item.product_id, LocationInventory.quantity > 0)
                .order_by(LocationInventory.quantity.desc())
                .first()
            )
            location_id = inv.location_id if inv else None
            if not location_id:
                loc = db.query(Location).first()
                location_id = loc.id if loc else 1

            sequence += 1
            db.add(PickingTask(
                wave_id=wave.id,
                order_id=order_id,
                product_id=item.product_id,
                source_location_id=location_id,
                requested_quantity=item.quantity,
                sequence=sequence,
            ))

    db.commit()
    return db.query(PickingWave).options(joinedload(PickingWave.tasks)).filter(PickingWave.id == wave.id).first()


@router.get("/{wave_id}", response_model=PickingWaveOut)
def get_wave(wave_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    wave = db.query(PickingWave).options(joinedload(PickingWave.tasks)).filter(PickingWave.id == wave_id).first()
    if not wave:
        raise HTTPException(status_code=404, detail="Wave non trovata")
    return wave


@router.post("/{wave_id}/start", response_model=PickingWaveOut)
def start_wave(wave_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    wave = db.query(PickingWave).filter(PickingWave.id == wave_id).first()
    if not wave:
        raise HTTPException(status_code=404, detail="Wave non trovata")
    if wave.status != "creato":
        raise HTTPException(status_code=400, detail="Wave non in stato avviabile")
    wave.status = "in_corso"
    wave.started_at = datetime.now(timezone.utc)
    if not wave.assigned_user_id:
        wave.assigned_user_id = current_user.id
    db.commit()
    return db.query(PickingWave).options(joinedload(PickingWave.tasks)).filter(PickingWave.id == wave_id).first()


@router.post("/{wave_id}/confirm", response_model=PickingWaveOut)
def confirm_picks(
    wave_id: int,
    picks: list[PickConfirm],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "responsabile", "magazziniere")),
):
    wave = db.query(PickingWave).filter(PickingWave.id == wave_id).first()
    if not wave:
        raise HTTPException(status_code=404, detail="Wave non trovata")

    for pick in picks:
        task = db.query(PickingTask).filter(PickingTask.id == pick.task_id, PickingTask.wave_id == wave_id).first()
        if not task:
            continue
        task.picked_quantity = pick.picked_quantity
        task.status = "completed" if pick.picked_quantity >= task.requested_quantity else "partial"
        task.picked_at = datetime.now(timezone.utc)
        task.picked_by = current_user.id

        inv = db.query(LocationInventory).filter(
            LocationInventory.location_id == task.source_location_id,
            LocationInventory.product_id == task.product_id,
        ).first()
        if inv:
            inv.quantity = max(0, inv.quantity - pick.picked_quantity)

    remaining = db.query(PickingTask).filter(
        PickingTask.wave_id == wave_id,
        PickingTask.status == "pending",
    ).count()
    if remaining == 0:
        wave.status = "completato"
        wave.completed_at = datetime.now(timezone.utc)

    db.commit()
    return db.query(PickingWave).options(joinedload(PickingWave.tasks)).filter(PickingWave.id == wave_id).first()


@router.delete("/{wave_id}", status_code=204)
def delete_wave(wave_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    wave = db.query(PickingWave).filter(PickingWave.id == wave_id).first()
    if not wave:
        raise HTTPException(status_code=404, detail="Wave non trovata")
    if wave.status == "completato":
        raise HTTPException(status_code=400, detail="Impossibile eliminare una wave completata")
    db.delete(wave)
    db.commit()
