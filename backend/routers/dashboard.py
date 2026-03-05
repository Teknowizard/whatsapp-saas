from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from core.security import get_current_user
from models.user import User
from services.analytics import get_user_analytics, get_revenue_by_day
from schemas.analytics import AnalyticsSummary

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsSummary)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_analytics(db, current_user.id)
