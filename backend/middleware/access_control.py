from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from core.security import decode_token
from database.session import SessionLocal
from models.user import User


class AccessControlMiddleware(BaseHTTPMiddleware):
    """Enforce subscription and suspension rules"""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip public routes
        if not path.startswith("/api/") or path in [
            "/api/login", "/api/register", "/api/health", "/api/config",
            "/api/webhook/paystack", "/api/webhook/whatsapp"
        ]:
            return await call_next(request)
        
        # Skip admin routes (handled by admin router)
        if path.startswith("/api/admin"):
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if not payload:
            return await call_next(request)
        
        user_id = payload.get("sub")
        if not user_id:
            return await call_next(request)
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                return await call_next(request)
            
            # Admin bypass
            if user.is_admin:
                return await call_next(request)
            
            # Check access using has_access() method
            if not user.has_access():
                if user.is_suspended:
                    return JSONResponse(
                        {"detail": "Account suspended. Contact support."},
                        status_code=403
                    )
                return JSONResponse(
                    {"detail": "Subscription expired. Please renew to continue."},
                    status_code=402
                )
            
            return await call_next(request)
        finally:
            db.close()
