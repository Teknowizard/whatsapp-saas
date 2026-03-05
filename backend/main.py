from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging, os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.session import engine
from models import User, Product, AutoReply, Order, Log
from database.session import Base
from routers import auth, products, autoreplies, orders, webhooks, dashboard, analytics, admin
from middleware.tier_enforcement import TierEnforcementMiddleware
from middleware.rate_limiter import RateLimitMiddleware
from middleware.access_control import AccessControlMiddleware
from core.config import settings
from services.cart_reminder import check_abandoned_carts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    os.makedirs("uploads", exist_ok=True)
    scheduler.add_job(check_abandoned_carts, "interval", minutes=15)
    scheduler.start()
    logger.info(f"{settings.APP_NAME} Platform Started")
    yield
    scheduler.shutdown()
    logger.info("Shutdown complete")


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description=f"{settings.COMPANY_NAME} - WhatsApp Sales Automation Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AccessControlMiddleware)
app.add_middleware(TierEnforcementMiddleware)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(autoreplies.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(admin.router, prefix="/api")  # NEW


@app.get("/api/health")
async def health():
    return {"status": "healthy", "app": settings.APP_NAME}


@app.get("/api/config")
async def get_public_config():
    """Public configuration for frontend"""
    return {
        "app_name": settings.APP_NAME,
        "company_name": settings.COMPANY_NAME,
        "support_email": settings.SUPPORT_EMAIL
    }
