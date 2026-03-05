from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Branding (Centralized)
    APP_NAME: str = "Zubo"
    COMPANY_NAME: str = "Zubo Technologies"
    WHATSAPP_DISPLAY_NAME: str = "Zubo Support"
    SUPPORT_EMAIL: str = "support@zubo.ng"

    # App
    DEBUG: bool = False
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/whatsapp_saas"

    # WhatsApp Cloud API
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "whatsapp_verify_token_123"

    # Paystack
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://yourdomain.com"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Cart reminder (minutes)
    CART_REMINDER_MINUTES: int = 30

    # Frontend URL (for payment callbacks)
    FRONTEND_URL: str = "https://yourdomain.com"

    class Config:
        env_file = ".env"


settings = Settings()
