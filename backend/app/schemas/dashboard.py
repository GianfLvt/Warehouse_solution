from pydantic import BaseModel


class DashboardStats(BaseModel):
    pending_orders: int
    daily_shipments: int
    low_stock_products: int
    monthly_revenue: float
    total_products: int
    total_customers: int
    active_picking_waves: int = 0
    pending_asns: int = 0
    open_anomalies: int = 0
    warehouse_utilization: float = 0.0


class LowStockProduct(BaseModel):
    id: int
    sku: str
    name: str
    quantity: int
    min_stock: int

    model_config = {"from_attributes": True}


class KPIMetrics(BaseModel):
    avg_picking_time_min: float = 0
    picking_error_rate: float = 0
    stock_turnover_ratio: float = 0
    shelf_utilization_pct: float = 0
    order_fulfillment_rate: float = 0
    avg_order_cycle_time_hours: float = 0
    inbound_accuracy_pct: float = 0
    on_time_delivery_pct: float = 0


class OperatorKPI(BaseModel):
    user_id: int
    user_name: str
    picks_completed: int = 0
    picks_errors: int = 0
    efficiency_score: float = 0
    avg_pick_time_sec: float = 0


class WarehouseHeatmapCell(BaseModel):
    zone_code: str
    aisle: str
    activity_count: int
    congestion_level: str
