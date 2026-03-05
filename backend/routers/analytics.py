from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from core.security import get_current_user
from models.user import User, TierEnum
from services.analytics import get_revenue_by_day
from utils.dependencies import require_tier

router = APIRouter()


@router.get("/analytics/revenue")
async def revenue_chart(
    days: int = 30,
    current_user: User = Depends(require_tier(TierEnum.growth)),
    db: Session = Depends(get_db)
):
    return get_revenue_by_day(db, current_user.id, days)
