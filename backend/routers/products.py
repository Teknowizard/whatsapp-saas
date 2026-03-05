from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os, uuid, aiofiles

from database.session import get_db
from core.security import get_current_user
from models.user import User
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from utils.dependencies import check_product_limit, get_product_limit
from services.analytics import log_action

router = APIRouter()


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_product_limit(db, current_user):
        limit = get_product_limit(current_user)
        raise HTTPException(
            status_code=403,
            detail=f"Product limit reached ({limit} products for {current_user.tier.value} tier). Upgrade to add more."
        )

    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")

    image_url = None
    if image:
        ext = image.filename.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format")
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = f"uploads/{filename}"
        async with aiofiles.open(filepath, "wb") as f:
            content = await image.read()
            await f.write(content)
        image_url = f"/uploads/{filename}"

    product = Product(
        user_id=current_user.id,
        name=name.strip(),
        price=price,
        description=description,
        image_url=image_url
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    log_action(db, current_user.id, "product_created", {"product_id": product.id, "name": name})
    return product


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Product).filter(Product.user_id == current_user.id).all()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    updates: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if updates.name is not None:
        product.name = updates.name.strip()
    if updates.price is not None:
        if updates.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be positive")
        product.price = updates.price
    if updates.description is not None:
        product.description = updates.description

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete image file if exists
    if product.image_url:
        filepath = product.image_url.lstrip("/")
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.delete(product)
    db.commit()
