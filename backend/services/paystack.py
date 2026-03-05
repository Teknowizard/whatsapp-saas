import httpx
import hashlib
import hmac
import json
import logging
from core.config import settings

logger = logging.getLogger(__name__)


class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = settings.PAYSTACK_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    async def initialize_transaction(
        self,
        email: str,
        amount: float,
        reference: str,
        metadata: dict = None
    ) -> dict:
        """Initialize a Paystack transaction and get payment link"""
        payload = {
            "email": email,
            "amount": int(amount * 100),  # Paystack uses kobo
            "reference": reference,
            "callback_url": f"{settings.FRONTEND_URL}/payment/callback",
            "metadata": metadata or {}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/transaction/initialize",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", {})
            except httpx.HTTPStatusError as e:
                logger.error(f"Paystack API error: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Paystack initialization failed: {e}")
                raise

    async def verify_transaction(self, reference: str) -> dict:
        """Verify a transaction by reference"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/transaction/verify/{reference}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json().get("data", {})
            except Exception as e:
                logger.error(f"Paystack verification failed: {e}")
                raise

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate Paystack webhook signature"""
        computed = hmac.new(
            self.secret_key.encode("utf-8"),
            payload,
            digestmod=hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(computed, signature)


paystack_service = PaystackService()
