from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, subqueryload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.package import Package, PackageItem
from app.models.user import User
from app.schemas.package import PackageCreate, PackageOut, PackageUpdate

router = APIRouter(prefix="/api/packages", tags=["packages"])


@router.get("", response_model=list[PackageOut])
def list_packages(order_id: int | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    q = db.query(Package).options(subqueryload(Package.items))
    if order_id:
        q = q.filter(Package.order_id == order_id)
    return q.order_by(Package.created_at.desc()).all()


@router.post("", response_model=PackageOut, status_code=201)
def create_package(data: PackageCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    pkg = Package(
        order_id=data.order_id,
        weight=data.weight,
        tracking_number=data.tracking_number,
        carrier=data.carrier,
    )
    db.add(pkg)
    db.flush()

    for item_data in data.items:
        db.add(PackageItem(package_id=pkg.id, **item_data.model_dump()))

    db.commit()
    return db.query(Package).options(joinedload(Package.items)).filter(Package.id == pkg.id).first()


@router.get("/{package_id}", response_model=PackageOut)
def get_package(package_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    pkg = db.query(Package).options(joinedload(Package.items)).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Collo non trovato")
    return pkg


@router.put("/{package_id}", response_model=PackageOut)
def update_package(package_id: int, data: PackageUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Collo non trovato")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pkg, field, value)
    db.commit()
    db.refresh(pkg)
    return db.query(Package).options(joinedload(Package.items)).filter(Package.id == pkg.id).first()


@router.delete("/{package_id}", status_code=204)
def delete_package(package_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Collo non trovato")
    db.delete(pkg)
    db.commit()
