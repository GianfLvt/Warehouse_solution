from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, subqueryload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.quote import Quote, QuoteItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.quote import QuoteCreate, QuoteOut, QuoteUpdateStatus

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

VALID_STATUSES = ["bozza", "inviato", "accettato", "rifiutato"]


@router.get("", response_model=list[QuoteOut])
def list_quotes(
    status: str | None = None,
    customer_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Quote).options(subqueryload(Quote.items).joinedload(QuoteItem.product), joinedload(Quote.customer))
    if status:
        q = q.filter(Quote.status == status)
    if customer_id:
        q = q.filter(Quote.customer_id == customer_id)
    return q.order_by(Quote.created_at.desc()).all()


@router.post("", response_model=QuoteOut, status_code=201)
def create_quote(data: QuoteCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    quote = Quote(
        customer_id=data.customer_id,
        user_id=current_user.id,
        notes=data.notes,
        valid_until=data.valid_until,
    )
    db.add(quote)
    db.flush()
    for item_data in data.items:
        db.add(QuoteItem(quote_id=quote.id, **item_data.model_dump()))
    db.commit()
    return db.query(Quote).options(
        joinedload(Quote.items).joinedload(QuoteItem.product),
        joinedload(Quote.customer),
    ).filter(Quote.id == quote.id).first()


@router.get("/{quote_id}", response_model=QuoteOut)
def get_quote(quote_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    quote = (
        db.query(Quote)
        .options(joinedload(Quote.items).joinedload(QuoteItem.product), joinedload(Quote.customer))
        .filter(Quote.id == quote_id)
        .first()
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Preventivo non trovato")
    return quote


@router.patch("/{quote_id}/status", response_model=QuoteOut)
def update_quote_status(quote_id: int, data: QuoteUpdateStatus, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Stato non valido. Valori: {', '.join(VALID_STATUSES)}")
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Preventivo non trovato")
    quote.status = data.status
    db.commit()
    return db.query(Quote).options(
        joinedload(Quote.items).joinedload(QuoteItem.product),
        joinedload(Quote.customer),
    ).filter(Quote.id == quote_id).first()


@router.post("/{quote_id}/convert", status_code=201)
def convert_to_order(quote_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    quote = db.query(Quote).options(joinedload(Quote.items)).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Preventivo non trovato")

    order = Order(customer_id=quote.customer_id, user_id=current_user.id, notes=f"Da preventivo #{quote.id}")
    db.add(order)
    db.flush()

    for qi in quote.items:
        db.add(OrderItem(order_id=order.id, product_id=qi.product_id, quantity=qi.quantity, unit_price=qi.unit_price))

    quote.status = "accettato"
    db.commit()
    return {"order_id": order.id}


@router.delete("/{quote_id}", status_code=204)
def delete_quote(quote_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Preventivo non trovato")
    db.delete(quote)
    db.commit()
