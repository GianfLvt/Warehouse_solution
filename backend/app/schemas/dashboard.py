from pydantic import BaseModel


class DashboardStats(BaseModel):
    pending_orders: int
    daily_shipments: int
    low_stock_products: int
    monthly_revenue: float
    total_products: int
    total_customers: int


class LowStockProduct(BaseModel):
    id: int
    sku: str
    name: str
    quantity: int
    min_stock: int

    model_config = {"from_attributes": True}
