from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.session import Base


class TierEnum(str, enum.Enum):
    starter = "starter"
    growth = "growth"
    pro = "pro"


class SubscriptionStatus(str, enum.Enum):
    trial = "trial"
    active = "active"
    expired = "expired"
    suspended = "suspended"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    tier = Column(Enum(TierEnum), default=TierEnum.starter, nullable=False)
    
    # Admin & Access Control
    is_admin = Column(Boolean, default=False, nullable=False)
    is_suspended = Column(Boolean, default=False, nullable=False)
    is_payment_exempt = Column(Boolean, default=False, nullable=False)
    
    # Subscription Management
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.trial, nullable=False)
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    plan = Column(String(50), default="free", nullable=False)  # free | pro | enterprise
    
    # WhatsApp Config
    whatsapp_phone_number_id = Column(String(100), nullable=True)
    whatsapp_access_token = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    products = relationship("Product", back_populates="owner", cascade="all, delete-orphan")
    autoreplies = relationship("AutoReply", back_populates="owner", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="owner", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="owner", cascade="all, delete-orphan")

    def has_access(self) -> bool:
        """Check if user has platform access"""
        if self.is_suspended:
            return False
        return self.is_payment_exempt or self.subscription_status == SubscriptionStatus.active
