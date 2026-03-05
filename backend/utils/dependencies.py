from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.session import get_db
from core.security import get_current_user
from models.user import User, TierEnum
from middleware.tier_enforcement import TIER_LIMITS


def require_tier(min_tier: TierEnum):
    """Dependency to require a minimum tier"""
    tier_order = {TierEnum.starter: 0, TierEnum.growth: 1, TierEnum.pro: 2}
    
    def tier_checker(current_user: User = Depends(get_current_user)):
        if tier_order.get(current_user.tier, 0) < tier_order.get(min_tier, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {min_tier.value} tier or higher"
            )
        return current_user
    
    return tier_checker


def check_product_limit(db: Session, user: User) -> bool:
    """Check if user can add more products based on tier"""
    from models.product import Product
    current_count = db.query(Product).filter(Product.user_id == user.id).count()
    limit = TIER_LIMITS[user.tier]["max_products"]
    if limit is None:
        return True  # Unlimited (Pro)
    return current_count < limit


def get_product_limit(user: User) -> int | None:
    return TIER_LIMITS[user.tier]["max_products"]
