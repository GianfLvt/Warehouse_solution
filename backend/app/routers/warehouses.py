from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.warehouse import DockSlot, Location, LocationInventory, Warehouse, WarehouseZone
from app.schemas.warehouse import (
    DockSlotCreate,
    DockSlotOut,
    LocationCreate,
    LocationInventoryOut,
    LocationOut,
    WarehouseCreate,
    WarehouseListOut,
    WarehouseOut,
    WarehouseUpdate,
    WarehouseZoneCreate,
    WarehouseZoneOut,
)

router = APIRouter(prefix="/api/warehouses", tags=["warehouses"])


@router.get("", response_model=list[WarehouseListOut])
def list_warehouses(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Warehouse).order_by(Warehouse.name).all()


@router.post("", response_model=WarehouseOut, status_code=201)
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    if db.query(Warehouse).filter(Warehouse.code == data.code).first():
        raise HTTPException(status_code=400, detail="Codice magazzino già esistente")
    warehouse = Warehouse(**data.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    wh = (
        db.query(Warehouse)
        .options(joinedload(Warehouse.zones).joinedload(WarehouseZone.locations), joinedload(Warehouse.dock_slots))
        .filter(Warehouse.id == warehouse_id)
        .first()
    )
    if not wh:
        raise HTTPException(status_code=404, detail="Magazzino non trovato")
    return wh


@router.put("/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(warehouse_id: int, data: WarehouseUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Magazzino non trovato")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(wh, field, value)
    db.commit()
    db.refresh(wh)
    return wh


@router.delete("/{warehouse_id}", status_code=204)
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Magazzino non trovato")
    db.delete(wh)
    db.commit()


@router.post("/{warehouse_id}/zones", response_model=WarehouseZoneOut, status_code=201)
def create_zone(warehouse_id: int, data: WarehouseZoneCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Magazzino non trovato")
    existing = db.query(WarehouseZone).filter(WarehouseZone.warehouse_id == warehouse_id, WarehouseZone.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Codice zona già esistente in questo magazzino")
    zone = WarehouseZone(warehouse_id=warehouse_id, **data.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.get("/{warehouse_id}/zones", response_model=list[WarehouseZoneOut])
def list_zones(warehouse_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(WarehouseZone)
        .options(joinedload(WarehouseZone.locations))
        .filter(WarehouseZone.warehouse_id == warehouse_id)
        .order_by(WarehouseZone.code)
        .all()
    )


@router.delete("/zones/{zone_id}", status_code=204)
def delete_zone(zone_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    zone = db.query(WarehouseZone).filter(WarehouseZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zona non trovata")
    db.delete(zone)
    db.commit()


@router.post("/locations", response_model=LocationOut, status_code=201)
def create_location(data: LocationCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    zone = db.query(WarehouseZone).filter(WarehouseZone.id == data.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zona non trovata")
    if db.query(Location).filter(Location.barcode == data.barcode).first():
        raise HTTPException(status_code=400, detail="Barcode ubicazione già esistente")
    loc = Location(**data.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.get("/locations", response_model=list[LocationOut])
def list_locations(
    zone_id: int | None = None,
    warehouse_id: int | None = None,
    location_type: str | None = None,
    skip: int = 0,
    limit: int = Query(default=200, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Location)
    if zone_id:
        q = q.filter(Location.zone_id == zone_id)
    elif warehouse_id:
        zone_ids = [z.id for z in db.query(WarehouseZone.id).filter(WarehouseZone.warehouse_id == warehouse_id).all()]
        q = q.filter(Location.zone_id.in_(zone_ids))
    if location_type:
        q = q.filter(Location.location_type == location_type)
    return q.order_by(Location.aisle, Location.rack, Location.level, Location.bin).offset(skip).limit(limit).all()


@router.get("/locations/lookup/{barcode}", response_model=LocationOut)
def lookup_location(barcode: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    loc = db.query(Location).filter(Location.barcode == barcode).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Ubicazione non trovata")
    return loc


@router.get("/locations/{location_id}", response_model=LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Ubicazione non trovata")
    return loc


@router.get("/locations/{location_id}/inventory", response_model=list[LocationInventoryOut])
def get_location_inventory(location_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(LocationInventory).filter(LocationInventory.location_id == location_id).all()


@router.post("/{warehouse_id}/docks", response_model=DockSlotOut, status_code=201)
def create_dock(warehouse_id: int, data: DockSlotCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Magazzino non trovato")
    dock = DockSlot(warehouse_id=warehouse_id, **data.model_dump())
    db.add(dock)
    db.commit()
    db.refresh(dock)
    return dock


@router.get("/{warehouse_id}/docks", response_model=list[DockSlotOut])
def list_docks(warehouse_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(DockSlot).filter(DockSlot.warehouse_id == warehouse_id).order_by(DockSlot.code).all()
