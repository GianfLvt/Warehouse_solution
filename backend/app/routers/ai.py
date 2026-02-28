import math
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.ai_forecast import AIForecast, AnomalyDetection, OperatorPerformance, SlottingSuggestion
from app.models.order import Order, OrderItem
from app.models.picking import PickingTask, PickingWave
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.models.warehouse import Location, LocationInventory
from app.schemas.ai_forecast import (
    AIForecastOut,
    AnomalyDetectionOut,
    OperatorPerformanceOut,
    SeasonalTrend,
    SlottingSuggestionOut,
    StockPrediction,
)

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/stock-predictions", response_model=list[StockPrediction])
def predict_stock(
    warehouse_id: int | None = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Product).filter(Product.is_active.is_(True))
    if warehouse_id:
        q = q.filter(Product.warehouse_id == warehouse_id)
    products = q.order_by(Product.quantity).limit(limit).all()

    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    predictions = []
    for p in products:
        outbound = (
            db.query(func.coalesce(func.sum(StockMovement.quantity), 0))
            .filter(
                StockMovement.product_id == p.id,
                StockMovement.movement_type == "scarico",
                StockMovement.created_at >= thirty_days_ago,
            )
            .scalar()
        )
        daily_demand = float(outbound) / 30.0 if outbound else 0
        predicted_30d = daily_demand * 30

        days_until_stockout = None
        if daily_demand > 0:
            days_until_stockout = int(p.quantity / daily_demand)

        reorder = p.quantity <= p.reorder_point or (days_until_stockout is not None and days_until_stockout < 14)
        suggested_qty = max(p.reorder_quantity, int(predicted_30d * 1.2)) if reorder else 0

        predictions.append(StockPrediction(
            product_id=p.id,
            product_name=p.name,
            current_stock=p.quantity,
            predicted_demand_30d=round(predicted_30d, 1),
            days_until_stockout=days_until_stockout,
            reorder_suggested=reorder,
            suggested_quantity=suggested_qty,
        ))

    predictions.sort(key=lambda x: x.days_until_stockout if x.days_until_stockout is not None else 9999)
    return predictions


@router.get("/seasonal-trends", response_model=list[SeasonalTrend])
def seasonal_trends(product_id: int | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    trends = []

    for month in range(1, 13):
        q = db.query(func.coalesce(func.sum(StockMovement.quantity), 0)).filter(
            StockMovement.movement_type == "scarico",
            func.extract("month", StockMovement.created_at) == month,
        )
        if product_id:
            q = q.filter(StockMovement.product_id == product_id)
        avg_demand = float(q.scalar() or 0)

        current_month = now.month
        trend = "stable"
        if month == current_month:
            trend = "current"
        elif avg_demand > 0:
            trend = "high" if month in [11, 12, 1, 6, 7] else "normal"

        trends.append(SeasonalTrend(
            month=month,
            avg_demand=round(avg_demand, 1),
            predicted_demand=round(avg_demand * 1.05, 1),
            trend=trend,
        ))

    return trends


@router.post("/run-slotting")
def run_slotting_analysis(
    warehouse_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "responsabile")),
):
    now = datetime.now(timezone.utc)
    ninety_days_ago = now - timedelta(days=90)

    product_movements = (
        db.query(
            StockMovement.product_id,
            func.count(StockMovement.id).label("movement_count"),
        )
        .filter(StockMovement.created_at >= ninety_days_ago)
        .group_by(StockMovement.product_id)
        .order_by(func.count(StockMovement.id).desc())
        .limit(50)
        .all()
    )

    suggestions_created = 0
    for pm in product_movements:
        product = db.query(Product).filter(Product.id == pm.product_id).first()
        if not product:
            continue

        current_inv = (
            db.query(LocationInventory)
            .filter(LocationInventory.product_id == pm.product_id, LocationInventory.quantity > 0)
            .first()
        )

        easy_access = (
            db.query(Location)
            .filter(Location.is_active.is_(True), Location.is_blocked.is_(False), Location.level.in_(["1", "2", "A", "B"]))
            .first()
        )

        if easy_access and current_inv and current_inv.location_id != easy_access.id:
            existing = db.query(SlottingSuggestion).filter(
                SlottingSuggestion.product_id == pm.product_id,
                SlottingSuggestion.status == "pending",
            ).first()
            if not existing:
                db.add(SlottingSuggestion(
                    product_id=pm.product_id,
                    current_location_id=current_inv.location_id,
                    suggested_location_id=easy_access.id,
                    reason="high_rotation",
                    priority_score=float(pm.movement_count),
                ))
                suggestions_created += 1

    db.commit()
    return {"suggestions_created": suggestions_created}


@router.get("/slotting-suggestions", response_model=list[SlottingSuggestionOut])
def list_slotting_suggestions(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(SlottingSuggestion)
    if status:
        q = q.filter(SlottingSuggestion.status == status)
    return q.order_by(SlottingSuggestion.priority_score.desc()).limit(50).all()


@router.get("/operator-performance", response_model=list[OperatorPerformanceOut])
def list_operator_performance(
    user_id: int | None = None,
    days: int = Query(default=7, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "responsabile")),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(OperatorPerformance).filter(OperatorPerformance.period_date >= cutoff)
    if user_id:
        q = q.filter(OperatorPerformance.user_id == user_id)
    return q.order_by(OperatorPerformance.period_date.desc()).all()


@router.post("/detect-anomalies")
def detect_anomalies(db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    anomalies_created = 0
    now = datetime.now(timezone.utc)

    low_stock = db.query(Product).filter(
        Product.is_active.is_(True),
        Product.quantity <= Product.min_stock,
        Product.quantity > 0,
    ).all()
    for p in low_stock:
        existing = db.query(AnomalyDetection).filter(
            AnomalyDetection.anomaly_type == "low_stock",
            AnomalyDetection.entity_type == "product",
            AnomalyDetection.entity_id == p.id,
            AnomalyDetection.status == "open",
        ).first()
        if not existing:
            db.add(AnomalyDetection(
                anomaly_type="low_stock",
                severity="high" if p.quantity == 0 else "medium",
                entity_type="product",
                entity_id=p.id,
                description=f"Prodotto {p.sku} sotto scorta: {p.quantity}/{p.min_stock}",
                suggested_action=f"Riordinare almeno {p.reorder_quantity or p.min_stock} unità",
            ))
            anomalies_created += 1

    stale_orders = db.query(Order).filter(
        Order.status.in_(["in_lavorazione", "in_preparazione"]),
        Order.created_at < now - timedelta(days=3),
    ).all()
    for o in stale_orders:
        existing = db.query(AnomalyDetection).filter(
            AnomalyDetection.anomaly_type == "stale_order",
            AnomalyDetection.entity_type == "order",
            AnomalyDetection.entity_id == o.id,
            AnomalyDetection.status == "open",
        ).first()
        if not existing:
            db.add(AnomalyDetection(
                anomaly_type="stale_order",
                severity="medium",
                entity_type="order",
                entity_id=o.id,
                description=f"Ordine #{o.id} fermo in stato '{o.status}' da oltre 3 giorni",
                suggested_action="Verificare e riprendere la lavorazione",
            ))
            anomalies_created += 1

    db.commit()
    return {"anomalies_detected": anomalies_created}


@router.get("/anomalies", response_model=list[AnomalyDetectionOut])
def list_anomalies(
    status: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(AnomalyDetection)
    if status:
        q = q.filter(AnomalyDetection.status == status)
    if severity:
        q = q.filter(AnomalyDetection.severity == severity)
    return q.order_by(AnomalyDetection.created_at.desc()).limit(100).all()


@router.get("/forecasts", response_model=list[AIForecastOut])
def list_forecasts(
    forecast_type: str | None = None,
    product_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(AIForecast)
    if forecast_type:
        q = q.filter(AIForecast.forecast_type == forecast_type)
    if product_id:
        q = q.filter(AIForecast.product_id == product_id)
    return q.order_by(AIForecast.created_at.desc()).limit(50).all()
