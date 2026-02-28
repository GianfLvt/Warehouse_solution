from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.lot import Lot, SerialNumber
from app.models.user import User
from app.schemas.lot import LotCreate, LotOut, SerialNumberCreate, SerialNumberOut

router = APIRouter(prefix="/api/lots", tags=["lots"])


@router.get("", response_model=list[LotOut])
def list_lots(
    product_id: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Lot)
    if product_id:
        q = q.filter(Lot.product_id == product_id)
    if status:
        q = q.filter(Lot.status == status)
    return q.order_by(Lot.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=LotOut, status_code=201)
def create_lot(data: LotCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    existing = db.query(Lot).filter(Lot.product_id == data.product_id, Lot.lot_number == data.lot_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lotto già esistente per questo prodotto")
    lot = Lot(**data.model_dump())
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@router.get("/{lot_id}", response_model=LotOut)
def get_lot(lot_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lotto non trovato")
    return lot


@router.get("/serials", response_model=list[SerialNumberOut])
def list_serials(
    product_id: int | None = None,
    lot_id: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(SerialNumber)
    if product_id:
        q = q.filter(SerialNumber.product_id == product_id)
    if lot_id:
        q = q.filter(SerialNumber.lot_id == lot_id)
    if status:
        q = q.filter(SerialNumber.status == status)
    return q.order_by(SerialNumber.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/serials", response_model=SerialNumberOut, status_code=201)
def create_serial(data: SerialNumberCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    if db.query(SerialNumber).filter(SerialNumber.serial == data.serial).first():
        raise HTTPException(status_code=400, detail="Numero seriale già esistente")
    sn = SerialNumber(**data.model_dump())
    db.add(sn)
    db.commit()
    db.refresh(sn)
    return sn


@router.get("/serials/lookup/{serial}", response_model=SerialNumberOut)
def lookup_serial(serial: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    sn = db.query(SerialNumber).filter(SerialNumber.serial == serial).first()
    if not sn:
        raise HTTPException(status_code=404, detail="Seriale non trovato")
    return sn
