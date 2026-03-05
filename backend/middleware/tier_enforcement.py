from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from core.security import decode_token
from database.session import SessionLocal
from models.user import TierEnum


TIER_LIMITS = {
    TierEnum.starter: {
        "max_products": 10,
        "payment_links": False,
        "analytics": False,
        "abandoned_cart": False,
        "broadcast": False,
        "multi_number": False,
    },
    TierEnum.growth: {
        "max_products": 30,
        "payment_links": True,
        "analytics": True,
        "abandoned_cart": False,
        "broadcast": False,
        "multi_number": False,
    },
    TierEnum.pro: {
        "max_products": None,  # Unlimited
        "payment_links": True,
        "analytics": True,
        "abandoned_cart": True,
        "broadcast": True,
        "multi_number": True,
    },
}

PRO_ONLY_ROUTES = ["/api/broadcast", "/api/reminders"]
GROWTH_PLUS_ROUTES = ["/api/analytics"]


class TierEnforcementMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip non-protected routes
        if not path.startswith("/api/") or path in [
            "/api/login", "/api/register", "/api/health",
            "/api/webhook/paystack", "/api/webhook/whatsapp"
        ]:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)

        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if not payload:
            return await call_next(request)

        user_tier = payload.get("tier", "starter")

        # Enforce Pro-only routes
        for route in PRO_ONLY_ROUTES:
            if path.startswith(route):
                if user_tier != TierEnum.pro:
                    return JSONResponse(
                        {"detail": "This feature requires Pro tier"},
                        status_code=403
                    )

        # Enforce Growth+ routes
        for route in GROWTH_PLUS_ROUTES:
            if path.startswith(route):
                if user_tier == TierEnum.starter:
                    return JSONResponse(
                        {"detail": "This feature requires Growth or Pro tier"},
                        status_code=403
                    )

        return await call_next(request)
