from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.user import TierEnum, SubscriptionStatus


class AdminStatsResponse(BaseModel):
    total_users: int
    active_subscriptions: int
    expired_users: int
    suspended_users: int
    total_messages_sent: int
    connected_whatsapp_sessions: int
    total_revenue: float


class AdminUserListResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    tier: TierEnum
    subscription_status: SubscriptionStatus
    is_suspended: bool
    is_payment_exempt: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    tier: TierEnum
    is_admin: bool
    is_suspended: bool
    is_payment_exempt: bool
    subscription_status: SubscriptionStatus
    subscription_expires_at: Optional[datetime]
    plan: str
    whatsapp_phone_number_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    is_suspended: Optional[bool] = None
    is_payment_exempt: Optional[bool] = None
    subscription_status: Optional[SubscriptionStatus] = None
    subscription_expires_at: Optional[datetime] = None
    plan: Optional[str] = None
    tier: Optional[TierEnum] = None
