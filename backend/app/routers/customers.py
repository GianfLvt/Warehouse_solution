from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.customer import Customer, CustomerAddress
from app.models.user import User
from app.schemas.customer import AddressCreate, AddressOut, CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut])
def list_customers(
    search: str | None = None,
    customer_type: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Customer)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            (Customer.contact_name.ilike(pattern))
            | (Customer.company_name.ilike(pattern))
            | (Customer.email.ilike(pattern))
        )
    if customer_type:
        q = q.filter(Customer.customer_type == customer_type)
    return q.order_by(Customer.contact_name).offset(skip).limit(limit).all()


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    addresses_data = data.addresses
    customer = Customer(**data.model_dump(exclude={"addresses"}))
    db.add(customer)
    db.flush()
    for addr in addresses_data:
        db.add(CustomerAddress(customer_id=customer.id, **addr.model_dump()))
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    db.delete(customer)
    db.commit()


@router.post("/{customer_id}/addresses", response_model=AddressOut, status_code=201)
def add_address(customer_id: int, data: AddressCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    if data.is_default:
        db.query(CustomerAddress).filter(CustomerAddress.customer_id == customer_id).update({"is_default": False})
    addr = CustomerAddress(customer_id=customer_id, **data.model_dump())
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/{customer_id}/addresses/{address_id}", status_code=204)
def delete_address(customer_id: int, address_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "commerciale"))):
    addr = db.query(CustomerAddress).filter(CustomerAddress.id == address_id, CustomerAddress.customer_id == customer_id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Indirizzo non trovato")
    db.delete(addr)
    db.commit()
