from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, subqueryload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderUpdateStatus

router = APIRouter(prefix="/api/orders", tags=["orders"])

VALID_STATUSES = ["in_lavorazione", "in_preparazione", "pronto", "spedito", "consegnato"]


@router.get("", response_model=list[OrderOut])
def list_orders(
    status: str | None = None,
    customer_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Order).options(subqueryload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer))
    if status:
        q = q.filter(Order.status == status)
    if customer_id:
        q = q.filter(Order.customer_id == customer_id)
    return q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    order = Order(
        customer_id=data.customer_id,
        address_id=data.address_id,
        user_id=current_user.id,
        notes=data.notes,
    )
    db.add(order)
    db.flush()

    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Prodotto {item_data.product_id} non trovato")
        db.add(OrderItem(order_id=order.id, **item_data.model_dump()))

    db.commit()
    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.customer),
    ).filter(Order.id == order.id).first()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Ordine non trovato")
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, data: OrderUpdateStatus, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Stato non valido. Valori: {', '.join(VALID_STATUSES)}")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ordine non trovato")

    if data.status == "spedito" and order.status != "spedito":
        for item in db.query(OrderItem).filter(OrderItem.order_id == order_id).all():
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.quantity = max(0, product.quantity - item.quantity)
                db.add(StockMovement(
                    product_id=product.id,
                    movement_type="scarico",
                    quantity=item.quantity,
                    notes=f"Ordine #{order.id}",
                    user_id=current_user.id,
                ))

    order.status = data.status
    db.commit()
    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.customer),
    ).filter(Order.id == order_id).first()


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ordine non trovato")
    db.delete(order)
    db.commit()
