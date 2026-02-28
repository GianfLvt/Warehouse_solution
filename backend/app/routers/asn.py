import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.asn import ASN, ASNItem
from app.models.lot import Lot
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.models.warehouse import LocationInventory
from app.schemas.asn import ASNCreate, ASNOut, ASNReceiveItem, ASNUpdateStatus

router = APIRouter(prefix="/api/asn", tags=["asn"])

VALID_STATUSES = ["atteso", "in_arrivo", "in_ricezione", "completato", "annullato"]


def generate_asn_number() -> str:
    return f"ASN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@router.get("", response_model=list[ASNOut])
def list_asns(
    status: str | None = None,
    warehouse_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(ASN).options(joinedload(ASN.items))
    if status:
        q = q.filter(ASN.status == status)
    if warehouse_id:
        q = q.filter(ASN.warehouse_id == warehouse_id)
    return q.order_by(ASN.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=ASNOut, status_code=201)
def create_asn(data: ASNCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    asn = ASN(
        asn_number=generate_asn_number(),
        supplier=data.supplier,
        warehouse_id=data.warehouse_id,
        dock_slot_id=data.dock_slot_id,
        expected_date=data.expected_date,
        carrier=data.carrier,
        tracking_number=data.tracking_number,
        notes=data.notes,
        user_id=current_user.id,
    )
    db.add(asn)
    db.flush()
    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Prodotto {item_data.product_id} non trovato")
        db.add(ASNItem(asn_id=asn.id, **item_data.model_dump()))
    db.commit()
    return db.query(ASN).options(joinedload(ASN.items)).filter(ASN.id == asn.id).first()


@router.get("/{asn_id}", response_model=ASNOut)
def get_asn(asn_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    asn = db.query(ASN).options(joinedload(ASN.items)).filter(ASN.id == asn_id).first()
    if not asn:
        raise HTTPException(status_code=404, detail="ASN non trovato")
    return asn


@router.patch("/{asn_id}/status", response_model=ASNOut)
def update_asn_status(asn_id: int, data: ASNUpdateStatus, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Stato non valido. Valori: {', '.join(VALID_STATUSES)}")
    asn = db.query(ASN).filter(ASN.id == asn_id).first()
    if not asn:
        raise HTTPException(status_code=404, detail="ASN non trovato")
    if data.status == "in_ricezione" and not asn.arrived_at:
        asn.arrived_at = datetime.now(timezone.utc)
    asn.status = data.status
    db.commit()
    return db.query(ASN).options(joinedload(ASN.items)).filter(ASN.id == asn_id).first()


@router.post("/{asn_id}/receive", response_model=ASNOut)
def receive_asn_items(
    asn_id: int,
    items: list[ASNReceiveItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "responsabile", "magazziniere")),
):
    asn = db.query(ASN).filter(ASN.id == asn_id).first()
    if not asn:
        raise HTTPException(status_code=404, detail="ASN non trovato")
    if asn.status not in ("in_ricezione", "in_arrivo", "atteso"):
        raise HTTPException(status_code=400, detail="ASN non in stato ricevibile")

    asn.status = "in_ricezione"
    if not asn.arrived_at:
        asn.arrived_at = datetime.now(timezone.utc)

    all_complete = True
    for receive in items:
        asn_item = db.query(ASNItem).filter(ASNItem.id == receive.asn_item_id, ASNItem.asn_id == asn_id).first()
        if not asn_item:
            raise HTTPException(status_code=400, detail=f"Item ASN {receive.asn_item_id} non trovato")

        asn_item.received_quantity += receive.received_quantity
        if asn_item.received_quantity >= asn_item.expected_quantity:
            asn_item.status = "ricevuto"
        else:
            asn_item.status = "parziale"
            all_complete = False

        product = db.query(Product).filter(Product.id == asn_item.product_id).first()
        if product:
            product.quantity += receive.received_quantity
            db.add(StockMovement(
                product_id=product.id,
                movement_type="carico",
                quantity=receive.received_quantity,
                notes=f"ASN #{asn.asn_number}",
                user_id=current_user.id,
            ))

        lot_number = receive.lot_number or asn_item.lot_number
        if lot_number and product and product.lot_tracking:
            lot = db.query(Lot).filter(Lot.product_id == product.id, Lot.lot_number == lot_number).first()
            if not lot:
                lot = Lot(product_id=product.id, lot_number=lot_number)
                db.add(lot)
                db.flush()

        location_id = receive.location_id or asn_item.target_location_id
        if location_id:
            inv = db.query(LocationInventory).filter(
                LocationInventory.location_id == location_id,
                LocationInventory.product_id == asn_item.product_id,
            ).first()
            if inv:
                inv.quantity += receive.received_quantity
            else:
                db.add(LocationInventory(
                    location_id=location_id,
                    product_id=asn_item.product_id,
                    quantity=receive.received_quantity,
                ))

    if all_complete:
        remaining = db.query(ASNItem).filter(ASNItem.asn_id == asn_id, ASNItem.status != "ricevuto").count()
        if remaining == 0:
            asn.status = "completato"
            asn.completed_at = datetime.now(timezone.utc)

    db.commit()
    return db.query(ASN).options(joinedload(ASN.items)).filter(ASN.id == asn_id).first()


@router.delete("/{asn_id}", status_code=204)
def delete_asn(asn_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    asn = db.query(ASN).filter(ASN.id == asn_id).first()
    if not asn:
        raise HTTPException(status_code=404, detail="ASN non trovato")
    if asn.status == "completato":
        raise HTTPException(status_code=400, detail="Impossibile eliminare un ASN completato")
    db.delete(asn)
    db.commit()
