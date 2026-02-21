from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.dashboard import DashboardStats, LowStockProduct

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    pending = db.query(func.count(Order.id)).filter(Order.status.in_(["in_lavorazione", "in_preparazione", "pronto"])).scalar()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_shipments = db.query(func.count(Order.id)).filter(
        Order.status == "spedito",
        Order.updated_at >= today_start,
    ).scalar()

    low_stock = db.query(func.count(Product.id)).filter(Product.quantity <= Product.min_stock).scalar()

    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_rev = (
        db.query(func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(["spedito", "consegnato"]), Order.created_at >= month_start)
        .scalar()
    )

    total_products = db.query(func.count(Product.id)).scalar()
    total_customers = db.query(func.count(Customer.id)).scalar()

    return DashboardStats(
        pending_orders=pending or 0,
        daily_shipments=daily_shipments or 0,
        low_stock_products=low_stock or 0,
        monthly_revenue=float(monthly_rev or 0),
        total_products=total_products or 0,
        total_customers=total_customers or 0,
    )


@router.get("/low-stock", response_model=list[LowStockProduct])
def get_low_stock(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(Product)
        .filter(Product.quantity <= Product.min_stock)
        .order_by(Product.quantity)
        .limit(20)
        .all()
    )


@router.get("/recent-orders")
def get_recent_orders(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    return [
        {
            "id": o.id,
            "customer_id": o.customer_id,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]
