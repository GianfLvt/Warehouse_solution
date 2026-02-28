from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.inventory import CycleCount, CycleCountItem, QualityCheck
from app.models.user import User
from app.models.warehouse import Location, LocationInventory, WarehouseZone
from app.schemas.inventory import (
    CountItemSubmit,
    CycleCountCreate,
    CycleCountOut,
    CycleCountItemOut,
    QualityCheckCreate,
    QualityCheckOut,
)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("/cycle-counts", response_model=list[CycleCountOut])
def list_cycle_counts(
    warehouse_id: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(CycleCount)
    if warehouse_id:
        q = q.filter(CycleCount.warehouse_id == warehouse_id)
    if status:
        q = q.filter(CycleCount.status == status)
    return q.order_by(CycleCount.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/cycle-counts", response_model=CycleCountOut, status_code=201)
def create_cycle_count(
    data: CycleCountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "responsabile", "magazziniere")),
):
    cc = CycleCount(
        warehouse_id=data.warehouse_id,
        zone_id=data.zone_id,
        count_type=data.count_type,
        scheduled_date=data.scheduled_date,
        assigned_user_id=data.assigned_user_id,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(cc)
    db.flush()

    if data.zone_id:
        zone_ids = [data.zone_id]
    else:
        zone_ids = [z.id for z in db.query(WarehouseZone.id).filter(WarehouseZone.warehouse_id == data.warehouse_id).all()]

    locations = db.query(Location).filter(Location.zone_id.in_(zone_ids), Location.is_active.is_(True)).all()
    total = 0
    for loc in locations:
        inventories = db.query(LocationInventory).filter(LocationInventory.location_id == loc.id).all()
        for inv in inventories:
            db.add(CycleCountItem(
                cycle_count_id=cc.id,
                location_id=loc.id,
                product_id=inv.product_id,
                lot_id=inv.lot_id,
                system_quantity=inv.quantity,
            ))
            total += 1

    cc.total_locations = total
    db.commit()
    db.refresh(cc)
    return cc


@router.get("/cycle-counts/{cc_id}", response_model=CycleCountOut)
def get_cycle_count(cc_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cc = db.query(CycleCount).filter(CycleCount.id == cc_id).first()
    if not cc:
        raise HTTPException(status_code=404, detail="Inventario non trovato")
    return cc


@router.get("/cycle-counts/{cc_id}/items", response_model=list[CycleCountItemOut])
def get_cycle_count_items(cc_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(CycleCountItem).filter(CycleCountItem.cycle_count_id == cc_id).all()


@router.post("/cycle-counts/{cc_id}/start", response_model=CycleCountOut)
def start_cycle_count(cc_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    cc = db.query(CycleCount).filter(CycleCount.id == cc_id).first()
    if not cc:
        raise HTTPException(status_code=404, detail="Inventario non trovato")
    cc.status = "in_corso"
    cc.started_at = datetime.now(timezone.utc)
    if not cc.assigned_user_id:
        cc.assigned_user_id = current_user.id
    db.commit()
    db.refresh(cc)
    return cc


@router.post("/cycle-counts/{cc_id}/submit", response_model=CycleCountOut)
def submit_counts(
    cc_id: int,
    counts: list[CountItemSubmit],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "responsabile", "magazziniere")),
):
    cc = db.query(CycleCount).filter(CycleCount.id == cc_id).first()
    if not cc:
        raise HTTPException(status_code=404, detail="Inventario non trovato")

    discrepancies = 0
    for count in counts:
        item = db.query(CycleCountItem).filter(CycleCountItem.id == count.count_item_id, CycleCountItem.cycle_count_id == cc_id).first()
        if not item:
            continue
        item.counted_quantity = count.counted_quantity
        item.variance = count.counted_quantity - item.system_quantity
        item.status = "counted"
        item.counted_at = datetime.now(timezone.utc)
        item.counted_by = current_user.id
        if item.variance != 0:
            discrepancies += 1

    cc.counted_locations += len(counts)
    cc.discrepancies += discrepancies

    remaining = db.query(CycleCountItem).filter(CycleCountItem.cycle_count_id == cc_id, CycleCountItem.status == "pending").count()
    if remaining == 0:
        cc.status = "completato"
        cc.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(cc)
    return cc


@router.get("/quality-checks", response_model=list[QualityCheckOut])
def list_quality_checks(
    reference_type: str | None = None,
    result: str | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(QualityCheck)
    if reference_type:
        q = q.filter(QualityCheck.reference_type == reference_type)
    if result:
        q = q.filter(QualityCheck.result == result)
    return q.order_by(QualityCheck.checked_at.desc()).offset(skip).limit(limit).all()


@router.post("/quality-checks", response_model=QualityCheckOut, status_code=201)
def create_quality_check(
    data: QualityCheckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "responsabile", "magazziniere")),
):
    qc = QualityCheck(checked_by=current_user.id, **data.model_dump())
    db.add(qc)
    db.commit()
    db.refresh(qc)
    return qc
