from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.iot import IoTDevice, RFIDScan, SensorReading
from app.models.user import User
from app.schemas.iot import (
    IoTDeviceCreate,
    IoTDeviceOut,
    IoTDeviceUpdate,
    RFIDScanCreate,
    RFIDScanOut,
    SensorReadingCreate,
    SensorReadingOut,
)

router = APIRouter(prefix="/api/iot", tags=["iot"])


@router.get("/devices", response_model=list[IoTDeviceOut])
def list_devices(
    warehouse_id: int | None = None,
    device_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(IoTDevice)
    if warehouse_id:
        q = q.filter(IoTDevice.warehouse_id == warehouse_id)
    if device_type:
        q = q.filter(IoTDevice.device_type == device_type)
    if status:
        q = q.filter(IoTDevice.status == status)
    return q.order_by(IoTDevice.name).all()


@router.post("/devices", response_model=IoTDeviceOut, status_code=201)
def create_device(data: IoTDeviceCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    if db.query(IoTDevice).filter(IoTDevice.device_code == data.device_code).first():
        raise HTTPException(status_code=400, detail="Codice dispositivo già esistente")
    device = IoTDevice(**data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/devices/{device_id}", response_model=IoTDeviceOut)
def get_device(device_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    d = db.query(IoTDevice).filter(IoTDevice.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dispositivo non trovato")
    return d


@router.put("/devices/{device_id}", response_model=IoTDeviceOut)
def update_device(device_id: int, data: IoTDeviceUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    d = db.query(IoTDevice).filter(IoTDevice.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dispositivo non trovato")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    db.commit()
    db.refresh(d)
    return d


@router.delete("/devices/{device_id}", status_code=204)
def delete_device(device_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    d = db.query(IoTDevice).filter(IoTDevice.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dispositivo non trovato")
    db.delete(d)
    db.commit()


@router.get("/readings", response_model=list[SensorReadingOut])
def list_readings(
    device_id: int | None = None,
    reading_type: str | None = None,
    alerts_only: bool = False,
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(SensorReading)
    if device_id:
        q = q.filter(SensorReading.device_id == device_id)
    if reading_type:
        q = q.filter(SensorReading.reading_type == reading_type)
    if alerts_only:
        q = q.filter(SensorReading.is_alert.is_(True))
    return q.order_by(SensorReading.recorded_at.desc()).offset(skip).limit(limit).all()


@router.post("/readings", response_model=SensorReadingOut, status_code=201)
def create_reading(data: SensorReadingCreate, db: Session = Depends(get_db)):
    device = db.query(IoTDevice).filter(IoTDevice.id == data.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo non trovato")
    device.last_seen = datetime.now(timezone.utc)
    device.status = "online"
    reading = SensorReading(**data.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.post("/rfid", response_model=RFIDScanOut, status_code=201)
def create_rfid_scan(data: RFIDScanCreate, db: Session = Depends(get_db)):
    scan = RFIDScan(**data.model_dump())
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


@router.get("/rfid", response_model=list[RFIDScanOut])
def list_rfid_scans(
    tag_id: str | None = None,
    device_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(RFIDScan)
    if tag_id:
        q = q.filter(RFIDScan.tag_id == tag_id)
    if device_id:
        q = q.filter(RFIDScan.device_id == device_id)
    return q.order_by(RFIDScan.scanned_at.desc()).offset(skip).limit(limit).all()
