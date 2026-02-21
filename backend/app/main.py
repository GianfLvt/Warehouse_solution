from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.dependencies import hash_password
from app.models import *  # noqa: F401, F403
from app.models.user import User
from app.routers import auth, customers, dashboard, orders, packages, products, quotes, stock_movements, supplier_orders, users


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
    title="WareHouse - Gestione Magazzino",
    version="1.0.0",
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


@app.get("/api/health")
def health():
    return {"status": "ok"}
