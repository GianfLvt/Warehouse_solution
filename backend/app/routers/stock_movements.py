from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.schemas.stock_movement import StockMovementCreate, StockMovementOut

router = APIRouter(prefix="/api/stock-movements", tags=["stock-movements"])

VALID_TYPES = ["carico", "scarico", "trasferimento", "reso"]


@router.get("", response_model=list[StockMovementOut])
def list_movements(
    product_id: int | None = None,
    movement_type: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(StockMovement)
    if product_id:
        q = q.filter(StockMovement.product_id == product_id)
    if movement_type:
        q = q.filter(StockMovement.movement_type == movement_type)
    return q.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=StockMovementOut, status_code=201)
def create_movement(data: StockMovementCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    if data.movement_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo non valido. Valori: {', '.join(VALID_TYPES)}")

    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")

    if data.movement_type in ("carico", "reso"):
        product.quantity += data.quantity
    elif data.movement_type == "scarico":
        product.quantity = max(0, product.quantity - data.quantity)
    elif data.movement_type == "trasferimento":
        pass

    movement = StockMovement(
        product_id=data.product_id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        notes=data.notes,
        user_id=current_user.id,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement
