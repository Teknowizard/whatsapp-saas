import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.session import SessionLocal
from models.order import Order, OrderStatus
from models.user import User, TierEnum
from models.product import Product
from services.whatsapp import WhatsAppService
from services.analytics import log_action
from core.config import settings

logger = logging.getLogger(__name__)


async def check_abandoned_carts():
    """Background task to check and send cart reminders (Pro only)"""
    db = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(minutes=settings.CART_REMINDER_MINUTES)
        
        pending_orders = (
            db.query(Order)
            .join(User, Order.user_id == User.id)
            .filter(
                Order.status == OrderStatus.pending,
                Order.payment_link.isnot(None),
                Order.created_at <= cutoff_time,
                Order.reminder_sent == 0,
                User.tier == TierEnum.pro
            )
            .all()
        )

        for order in pending_orders:
            try:
                user = db.query(User).filter(User.id == order.user_id).first()
                product = db.query(Product).filter(Product.id == order.product_id).first()
                
                if not user or not product:
                    continue

                whatsapp = WhatsAppService(
                    phone_number_id=user.whatsapp_phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID,
                    access_token=user.whatsapp_access_token or settings.WHATSAPP_ACCESS_TOKEN
                )

                await whatsapp.send_cart_reminder(
                    to=order.customer_phone,
                    product_name=product.name,
                    amount=order.amount,
                    payment_link=order.payment_link
                )

                order.reminder_sent = 1
                db.commit()

                log_action(db, order.user_id, "cart_reminder_sent", {
                    "order_id": order.id,
                    "customer_phone": order.customer_phone
                })

                logger.info(f"Cart reminder sent for order {order.id}")

            except Exception as e:
                logger.error(f"Failed to send reminder for order {order.id}: {e}")

    finally:
        db.close()
