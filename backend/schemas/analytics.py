from pydantic import BaseModel
from typing import List


class AnalyticsSummary(BaseModel):
    total_revenue: float
    total_orders: int
    pending_payments: int
    messages_handled: int
    conversion_rate: float
    paid_orders: int
    cancelled_orders: int
    delivered_orders: int


class RevenueByDay(BaseModel):
    date: str
    revenue: float
    orders: int
