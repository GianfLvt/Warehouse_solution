from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ai_forecast import AnomalyDetection, OperatorPerformance
from app.models.asn import ASN
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.picking import PickingTask, PickingWave
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.models.warehouse import Location, LocationInventory
from app.schemas.dashboard import DashboardStats, KPIMetrics, LowStockProduct, OperatorKPI, WarehouseHeatmapCell

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

    active_waves = db.query(func.count(PickingWave.id)).filter(PickingWave.status.in_(["creato", "in_corso"])).scalar()
    pending_asns = db.query(func.count(ASN.id)).filter(ASN.status.in_(["atteso", "in_arrivo"])).scalar()
    open_anomalies = db.query(func.count(AnomalyDetection.id)).filter(AnomalyDetection.status == "open").scalar()

    total_locations = db.query(func.count(Location.id)).filter(Location.is_active.is_(True)).scalar() or 1
    occupied = db.query(func.count(LocationInventory.id.distinct())).filter(LocationInventory.quantity > 0).scalar() or 0
    utilization = round((occupied / total_locations) * 100, 1)

    return DashboardStats(
        pending_orders=pending or 0,
        daily_shipments=daily_shipments or 0,
        low_stock_products=low_stock or 0,
        monthly_revenue=float(monthly_rev or 0),
        total_products=total_products or 0,
        total_customers=total_customers or 0,
        active_picking_waves=active_waves or 0,
        pending_asns=pending_asns or 0,
        open_anomalies=open_anomalies or 0,
        warehouse_utilization=utilization,
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


@router.get("/kpi", response_model=KPIMetrics)
def get_kpi(days: int = Query(default=30, le=365), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    avg_pick_time = (
        db.query(func.avg(OperatorPerformance.avg_pick_time_sec))
        .filter(OperatorPerformance.period_date >= cutoff)
        .scalar()
    )

    total_picks = db.query(func.sum(OperatorPerformance.picks_completed)).filter(OperatorPerformance.period_date >= cutoff).scalar() or 1
    total_errors = db.query(func.sum(OperatorPerformance.picks_errors)).filter(OperatorPerformance.period_date >= cutoff).scalar() or 0
    error_rate = round((total_errors / total_picks) * 100, 2) if total_picks else 0

    total_out = db.query(func.sum(StockMovement.quantity)).filter(
        StockMovement.movement_type == "scarico",
        StockMovement.created_at >= cutoff,
    ).scalar() or 0
    avg_stock = db.query(func.avg(Product.quantity)).scalar() or 1
    turnover = round(total_out / avg_stock, 2) if avg_stock else 0

    total_locations = db.query(func.count(Location.id)).filter(Location.is_active.is_(True)).scalar() or 1
    occupied = db.query(func.count(LocationInventory.location_id.distinct())).filter(LocationInventory.quantity > 0).scalar() or 0
    shelf_util = round((occupied / total_locations) * 100, 1)

    total_orders = db.query(func.count(Order.id)).filter(Order.created_at >= cutoff).scalar() or 1
    fulfilled = db.query(func.count(Order.id)).filter(
        Order.status.in_(["spedito", "consegnato"]),
        Order.created_at >= cutoff,
    ).scalar() or 0
    fulfillment_rate = round((fulfilled / total_orders) * 100, 1)

    return KPIMetrics(
        avg_picking_time_min=round(float(avg_pick_time or 0) / 60, 1),
        picking_error_rate=error_rate,
        stock_turnover_ratio=turnover,
        shelf_utilization_pct=shelf_util,
        order_fulfillment_rate=fulfillment_rate,
        avg_order_cycle_time_hours=0,
        inbound_accuracy_pct=0,
        on_time_delivery_pct=0,
    )


@router.get("/operator-kpi", response_model=list[OperatorKPI])
def get_operator_kpi(days: int = Query(default=7, le=90), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    results = (
        db.query(
            OperatorPerformance.user_id,
            func.sum(OperatorPerformance.picks_completed).label("picks"),
            func.sum(OperatorPerformance.picks_errors).label("errors"),
            func.avg(OperatorPerformance.efficiency_score).label("eff"),
            func.avg(OperatorPerformance.avg_pick_time_sec).label("avg_time"),
        )
        .filter(OperatorPerformance.period_date >= cutoff)
        .group_by(OperatorPerformance.user_id)
        .all()
    )

    kpis = []
    for r in results:
        user = db.query(User).filter(User.id == r.user_id).first()
        name = f"{user.first_name} {user.last_name}" if user else "N/A"
        kpis.append(OperatorKPI(
            user_id=r.user_id,
            user_name=name,
            picks_completed=int(r.picks or 0),
            picks_errors=int(r.errors or 0),
            efficiency_score=round(float(r.eff or 0), 1),
            avg_pick_time_sec=round(float(r.avg_time or 0), 1),
        ))

    return kpis


@router.get("/heatmap")
def get_heatmap(warehouse_id: int | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    results = (
        db.query(
            Location.aisle,
            func.count(StockMovement.id).label("activity"),
        )
        .join(LocationInventory, LocationInventory.location_id == Location.id)
        .join(StockMovement, StockMovement.product_id == LocationInventory.product_id)
        .filter(StockMovement.created_at >= cutoff)
        .group_by(Location.aisle)
        .all()
    )
    cells = []
    for r in results:
        level = "low" if r.activity < 5 else ("medium" if r.activity < 15 else "high")
        cells.append({
            "zone_code": "",
            "aisle": r.aisle,
            "activity_count": r.activity,
            "congestion_level": level,
        })
    return cells
