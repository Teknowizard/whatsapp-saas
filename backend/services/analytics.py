from sqlalchemy.orm import Session
from sqlalchemy import func
from models.order import Order, OrderStatus
from models.log import Log
from datetime import datetime, timedelta
import json


def log_action(db: Session, user_id: int, action_type: str, details: dict = None):
    """Create a log entry"""
    log = Log(
        user_id=user_id,
        type=action_type,
        details=details or {}
    )
    db.add(log)
    db.commit()


def get_user_analytics(db: Session, user_id: int) -> dict:
    """Get analytics summary for a user"""
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    
    total_revenue = sum(o.amount for o in orders if o.status == OrderStatus.paid)
    total_orders = len(orders)
    pending = sum(1 for o in orders if o.status == OrderStatus.pending)
    paid = sum(1 for o in orders if o.status == OrderStatus.paid)
    delivered = sum(1 for o in orders if o.status == OrderStatus.delivered)
    cancelled = sum(1 for o in orders if o.status == OrderStatus.cancelled)
    
    messages_handled = db.query(Log).filter(
        Log.user_id == user_id,
        Log.type == "message_received"
    ).count()

    conversion_rate = (paid / total_orders * 100) if total_orders > 0 else 0.0

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "pending_payments": pending,
        "messages_handled": messages_handled,
        "conversion_rate": round(conversion_rate, 2),
        "paid_orders": paid,
        "cancelled_orders": cancelled,
        "delivered_orders": delivered
    }


def get_revenue_by_day(db: Session, user_id: int, days: int = 30) -> list:
    """Get daily revenue for chart data"""
    result = []
    today = datetime.utcnow().date()
    
    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        day_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.paid,
            Order.created_at >= day_start,
            Order.created_at <= day_end
        ).all()
        
        result.append({
            "date": day.strftime("%Y-%m-%d"),
            "revenue": sum(o.amount for o in day_orders),
            "orders": len(day_orders)
        })
    
    return result
