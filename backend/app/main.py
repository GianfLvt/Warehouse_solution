from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.dependencies import hash_password
from app.models import *  # noqa: F401, F403
from app.models.user import User
from app.routers import (
    ai,
    asn,
    auth,
    customers,
    dashboard,
    integrations,
    inventory,
    iot,
    lots,
    orders,
    packages,
    picking,
    products,
    quotes,
    shipments,
    stock_movements,
    supplier_orders,
    users,
    warehouses,
)
from app.websocket import manager as ws_manager


def seed_admin():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@warehouse.local").first():
            db.add(User(
                email="admin@warehouse.local",
                password_hash=hash_password("Admin2026!"),
                first_name="Admin",
                last_name="System",
                role="admin",
            ))
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_admin()
    yield


app = FastAPI(
    title="WareHouse WMS 4.0 - Gestione Magazzino",
    version="4.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Existing routers ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(packages.router)
app.include_router(stock_movements.router)
app.include_router(supplier_orders.router)
app.include_router(quotes.router)
app.include_router(dashboard.router)

# --- WMS 4.0 routers ---
app.include_router(warehouses.router)
app.include_router(lots.router)
app.include_router(asn.router)
app.include_router(picking.router)
app.include_router(shipments.router)
app.include_router(iot.router)
app.include_router(integrations.router)
app.include_router(inventory.router)
app.include_router(ai.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "4.0.0"}


# --- WebSocket endpoint ---
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    await ws_manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast(channel, {"type": "message", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
