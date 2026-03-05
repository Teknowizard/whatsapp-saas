from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from database.session import get_db
from core.security import get_current_user
from models.user import User, TierEnum
from models.order import Order, OrderStatus
from models.product import Product
from schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from services.paystack import paystack_service
from services.whatsapp import WhatsAppService
from services.analytics import log_action

router = APIRouter()


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == data.product_id, Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    amount = data.amount or product.price
    reference = f"WSA-{uuid.uuid4().hex[:12].upper()}"

    order = Order(
        user_id=current_user.id,
        product_id=product.id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        amount=amount,
        payment_reference=reference,
        status=OrderStatus.pending
    )

    # Generate payment link if Growth or Pro tier
    if current_user.tier in [TierEnum.growth, TierEnum.pro]:
        try:
            paystack_data = await paystack_service.initialize_transaction(
                email=f"{data.customer_phone.replace('+', '')}@whatsapp.customer",
                amount=amount,
                reference=reference,
                metadata={
                    "user_id": current_user.id,
                    "product_id": product.id,
                    "customer_name": data.customer_name,
                    "customer_phone": data.customer_phone
                }
            )
            order.payment_link = paystack_data.get("authorization_url")

            # Send payment link via WhatsApp
            whatsapp = WhatsAppService(
                phone_number_id=current_user.whatsapp_phone_number_id,
                access_token=current_user.whatsapp_access_token
            )
            await whatsapp.send_payment_link(
                to=data.customer_phone,
                product_name=product.name,
                amount=amount,
                payment_link=order.payment_link
            )
        except Exception as e:
            pass  # Log but don't fail order creation

    db.add(order)
    db.commit()
    db.refresh(order)

    log_action(db, current_user.id, "order_created", {
        "order_id": order.id,
        "customer": data.customer_name,
        "amount": amount
    })

    return order


@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Order).filter(Order.user_id == current_user.id)
    if status_filter:
        try:
            status_enum = OrderStatus(status_filter)
            query = query.filter(Order.status == status_enum)
        except ValueError:
            pass
    return query.order_by(Order.created_at.desc()).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = update.status
    db.commit()
    db.refresh(order)
    return order
