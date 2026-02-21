import io

import barcode
from barcode.writer import ImageWriter
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import qrcode
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    search: str | None = None,
    category: str | None = None,
    low_stock: bool = False,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Product)
    if search:
        pattern = f"%{search}%"
        q = q.filter((Product.name.ilike(pattern)) | (Product.sku.ilike(pattern)) | (Product.barcode.ilike(pattern)))
    if category:
        q = q.filter(Product.category == category)
    if low_stock:
        q = q.filter(Product.quantity <= Product.min_stock)
    return q.order_by(Product.name).offset(skip).limit(limit).all()


@router.post("", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(status_code=400, detail="SKU già esistente")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(Product.category).filter(Product.category.isnot(None)).distinct().all()
    return sorted([r[0] for r in rows])


@router.get("/lookup/{code}", response_model=ProductOut)
def lookup_by_code(code: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.query(Product).filter(
        (Product.barcode == code) | (Product.sku == code)
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato per questo codice")
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile", "magazziniere"))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    updates = data.model_dump(exclude_unset=True)
    if "sku" in updates and updates["sku"] != product.sku:
        if db.query(Product).filter(Product.sku == updates["sku"]).first():
            raise HTTPException(status_code=400, detail="SKU già esistente")
    for field, value in updates.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "responsabile"))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    db.delete(product)
    db.commit()


@router.get("/{product_id}/barcode")
def generate_barcode(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    code_value = product.barcode or product.sku
    buf = io.BytesIO()
    code128 = barcode.get("code128", code_value, writer=ImageWriter())
    code128.write(buf, options={"module_width": 0.4, "module_height": 15, "font_size": 10, "text_distance": 5, "quiet_zone": 6})
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png", headers={"Content-Disposition": f'inline; filename="barcode-{product.sku}.png"'})


@router.get("/{product_id}/qrcode")
def generate_qrcode(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    code_value = product.barcode or product.sku
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(code_value)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png", headers={"Content-Disposition": f'inline; filename="qrcode-{product.sku}.png"'})
