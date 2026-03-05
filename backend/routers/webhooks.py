from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import json, hashlib, hmac, logging

from database.session import get_db
from models.order import Order, OrderStatus
from models.autoreply import AutoReply
from models.user import User
from services.whatsapp import WhatsAppService
from services.paystack import paystack_service
from services.analytics import log_action
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/webhook/whatsapp")
async def whatsapp_verify(request: Request):
    """WhatsApp webhook verification"""
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified")
        return int(challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming WhatsApp messages"""
    try:
        payload = await request.json()
        whatsapp_svc = WhatsAppService()
        message_data = whatsapp_svc.parse_incoming_message(payload)
        
        if not message_data or message_data["type"] != "text":
            return {"status": "ok"}

        sender_phone = message_data["from"]
        message_text = message_data["text"].lower().strip()
        phone_number_id = message_data.get("phone_number_id")

        # Find the user associated with this phone number
        user = None
        if phone_number_id:
            user = db.query(User).filter(
                User.whatsapp_phone_number_id == phone_number_id
            ).first()

        if not user:
            return {"status": "ok"}

        # Log incoming message
        log_action(db, user.id, "message_received", {
            "from": sender_phone,
            "message": message_text[:500]
        })

        # Match keywords for auto-reply
        autoreplies = db.query(AutoReply).filter(AutoReply.user_id == user.id).all()
        matched_response = None

        for reply in autoreplies:
            if reply.keyword in message_text or message_text in reply.keyword:
                matched_response = reply.response
                break

        if matched_response:
            whatsapp = WhatsAppService(
                phone_number_id=user.whatsapp_phone_number_id,
                access_token=user.whatsapp_access_token
            )
            await whatsapp.send_text_message(sender_phone, matched_response)
            log_action(db, user.id, "auto_reply_sent", {
                "to": sender_phone,
                "response_length": len(matched_response)
            })

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return {"status": "error"}


@router.post("/webhook/paystack")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Paystack payment notifications"""
    signature = request.headers.get("x-paystack-signature", "")
    body = await request.body()

    if not paystack_service.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = json.loads(body)
        event = payload.get("event")
        data = payload.get("data", {})

        if event == "charge.success":
            reference = data.get("reference")
            order = db.query(Order).filter(
                Order.payment_reference == reference
            ).first()

            if order and order.status == OrderStatus.pending:
                order.status = OrderStatus.paid
                db.commit()

                # Get user and product for confirmation message
                user = db.query(User).filter(User.id == order.user_id).first()
                if user:
                    from models.product import Product
                    product = db.query(Product).filter(Product.id == order.product_id).first()
                    product_name = product.name if product else "your order"

                    try:
                        whatsapp = WhatsAppService(
                            phone_number_id=user.whatsapp_phone_number_id,
                            access_token=user.whatsapp_access_token
                        )
                        await whatsapp.send_order_confirmation(
                            to=order.customer_phone,
                            product_name=product_name,
                            reference=reference
                        )
                    except Exception as e:
                        logger.error(f"Failed to send payment confirmation: {e}")

                    log_action(db, order.user_id, "payment_received", {
                        "order_id": order.id,
                        "reference": reference,
                        "amount": order.amount
                    })

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Paystack webhook error: {e}")
        return {"status": "error"}
