from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, subqueryload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.supplier_order import SupplierOrder, SupplierOrderItem
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.schemas.supplier_order import SupplierOrderCreate, SupplierOrderOut, SupplierOrderUpdateStatus

router = APIRouter(prefix="/api/supplier-orders", tags=["supplier-orders"])

VALID_STATUSES = ["inviato", "ricevuto", "parziale"]


@router.get("", response_model=list[SupplierOrderOut])
def list_supplier_orders(
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(SupplierOrder).options(subqueryload(SupplierOrder.items).joinedload(SupplierOrderItem.product))
    if status:
        q = q.filter(SupplierOrder.status == status)
    return q.order_by(SupplierOrder.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=SupplierOrderOut, status_code=201)
def create_supplier_order(data: SupplierOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    order = SupplierOrder(supplier=data.supplier, notes=data.notes, user_id=current_user.id)
    db.add(order)
    db.flush()
    for item_data in data.items:
        db.add(SupplierOrderItem(order_id=order.id, **item_data.model_dump()))
    db.commit()
    return db.query(SupplierOrder).options(
        joinedload(SupplierOrder.items).joinedload(SupplierOrderItem.product)
    ).filter(SupplierOrder.id == order.id).first()


@router.get("/{order_id}", response_model=SupplierOrderOut)
def get_supplier_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    order = (
        db.query(SupplierOrder)
        .options(joinedload(SupplierOrder.items).joinedload(SupplierOrderItem.product))
        .filter(SupplierOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Ordine fornitore non trovato")
    return order


@router.patch("/{order_id}/status", response_model=SupplierOrderOut)
def update_status(order_id: int, data: SupplierOrderUpdateStatus, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Stato non valido. Valori: {', '.join(VALID_STATUSES)}")
    order = db.query(SupplierOrder).filter(SupplierOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ordine fornitore non trovato")

    if data.status == "ricevuto" and order.status != "ricevuto":
        for item in db.query(SupplierOrderItem).filter(SupplierOrderItem.order_id == order_id).all():
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.quantity += item.quantity
                db.add(StockMovement(
                    product_id=product.id,
                    movement_type="carico",
                    quantity=item.quantity,
                    notes=f"Ordine fornitore #{order.id}",
                    user_id=current_user.id,
                ))

    order.status = data.status
    db.commit()
    return db.query(SupplierOrder).options(
        joinedload(SupplierOrder.items).joinedload(SupplierOrderItem.product)
    ).filter(SupplierOrder.id == order_id).first()


@router.delete("/{order_id}", status_code=204)
def delete_supplier_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    order = db.query(SupplierOrder).filter(SupplierOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ordine fornitore non trovato")
    db.delete(order)
    db.commit()
