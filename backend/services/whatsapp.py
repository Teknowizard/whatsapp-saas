import httpx
import logging
from core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self, phone_number_id: str = None, access_token: str = None):
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.base_url = f"{settings.WHATSAPP_API_URL}/{self.phone_number_id}/messages"

    async def send_text_message(self, to: str, message: str) -> dict:
        """Send a text message via WhatsApp Cloud API"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": message}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Message sent to {to}")
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp API error: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Failed to send WhatsApp message: {e}")
                raise

    async def send_payment_link(self, to: str, product_name: str, amount: float, payment_link: str) -> dict:
        message = (
            f"🛒 *Order Confirmation*\n\n"
            f"Product: {product_name}\n"
            f"Amount: ₦{amount:,.2f}\n\n"
            f"Complete your payment here:\n{payment_link}\n\n"
            f"_Payment link expires in 24 hours._"
        )
        return await self.send_text_message(to, message)

    async def send_cart_reminder(self, to: str, product_name: str, amount: float, payment_link: str) -> dict:
        message = (
            f"⏰ *Payment Reminder*\n\n"
            f"Hi! You have an incomplete order:\n"
            f"Product: {product_name}\n"
            f"Amount: ₦{amount:,.2f}\n\n"
            f"Complete your payment here:\n{payment_link}\n\n"
            f"_Don't miss out!_"
        )
        return await self.send_text_message(to, message)

    async def send_order_confirmation(self, to: str, product_name: str, reference: str) -> dict:
        message = (
            f"✅ *Payment Confirmed!*\n\n"
            f"Thank you! Your payment for *{product_name}* has been received.\n"
            f"Reference: {reference}\n\n"
            f"Your order is being processed. We'll notify you when it's ready!"
        )
        return await self.send_text_message(to, message)

    @staticmethod
    def parse_incoming_message(payload: dict) -> dict | None:
        """Extract message data from WhatsApp webhook payload"""
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return None
            msg = messages[0]
            contact = value.get("contacts", [{}])[0]
            return {
                "from": msg.get("from"),
                "name": contact.get("profile", {}).get("name", "Customer"),
                "message_id": msg.get("id"),
                "type": msg.get("type"),
                "text": msg.get("text", {}).get("body", "") if msg.get("type") == "text" else "",
                "phone_number_id": value.get("metadata", {}).get("phone_number_id")
            }
        except Exception as e:
            logger.error(f"Error parsing WhatsApp message: {e}")
            return None
