from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from database.session import get_db
from core.security import get_current_user
from models.user import User, SubscriptionStatus
from models.order import Order, OrderStatus
from models.log import Log
from schemas.admin import (
    AdminUserResponse, AdminUserUpdate, AdminStatsResponse,
    AdminUserListResponse
)

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to enforce admin-only access"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/admin/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics"""
    total_users = db.query(User).filter(User.is_admin == False).count()
    active_subs = db.query(User).filter(
        User.subscription_status == SubscriptionStatus.active,
        User.is_admin == False
    ).count()
    expired_users = db.query(User).filter(
        User.subscription_status == SubscriptionStatus.expired,
        User.is_admin == False
    ).count()
    suspended_users = db.query(User).filter(
        User.is_suspended == True,
        User.is_admin == False
    ).count()
    
    total_messages = db.query(Log).filter(
        Log.type == "message_received"
    ).count()
    
    total_revenue = db.query(func.sum(Order.amount)).filter(
        Order.status == OrderStatus.paid
    ).scalar() or 0
    
    connected_whatsapp = db.query(User).filter(
        User.whatsapp_phone_number_id.isnot(None),
        User.is_admin == False
    ).count()

    return {
        "total_users": total_users,
        "active_subscriptions": active_subs,
        "expired_users": expired_users,
        "suspended_users": suspended_users,
        "total_messages_sent": total_messages,
        "connected_whatsapp_sessions": connected_whatsapp,
        "total_revenue": total_revenue
    }


@router.get("/admin/users", response_model=List[AdminUserListResponse])
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users with filters"""
    query = db.query(User).filter(User.is_admin == False)
    
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.phone.ilike(f"%{search}%"))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/admin/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/admin/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    updates: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user account settings"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_admin:
        raise HTTPException(status_code=404, detail="User not found")
    
    if updates.is_suspended is not None:
        user.is_suspended = updates.is_suspended
    if updates.is_payment_exempt is not None:
        user.is_payment_exempt = updates.is_payment_exempt
    if updates.subscription_status is not None:
        user.subscription_status = updates.subscription_status
    if updates.subscription_expires_at is not None:
        user.subscription_expires_at = updates.subscription_expires_at
    if updates.plan is not None:
        user.plan = updates.plan
    if updates.tier is not None:
        user.tier = updates.tier
    
    db.commit()
    db.refresh(user)
    return user


@router.post("/admin/users/{user_id}/grant-access")
async def grant_free_access(
    user_id: int,
    days: int = 30,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Grant free access to a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_admin:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_payment_exempt = True
    user.subscription_status = SubscriptionStatus.active
    user.subscription_expires_at = datetime.utcnow() + timedelta(days=days)
    
    db.commit()
    return {"message": f"Free access granted for {days} days", "user_id": user_id}


@router.post("/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Suspend a user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_admin:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_suspended = True
    user.subscription_status = SubscriptionStatus.suspended
    db.commit()
    return {"message": "User suspended", "user_id": user_id}


@router.post("/admin/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reactivate a suspended user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_admin:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_suspended = False
    if user.subscription_status == SubscriptionStatus.suspended:
        user.subscription_status = SubscriptionStatus.active
    db.commit()
    return {"message": "User reactivated", "user_id": user_id}


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user account (use with caution)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_admin:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted", "user_id": user_id}
