import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.models import *  # ensure all models are imported so metadata is populated
from app.core.database import Base
from app.utils.logger import setup_logging, get_logger
from app.routers import auth, companies, users, shipments, drivers, warehouses, dashboard, notifications
from app.simulation.engine import simulation_loop

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Seed default roles on first run
        await conn.execute(text("""
            INSERT INTO roles (name, description) VALUES
              ('super_admin', 'Full system access'),
              ('company_admin', 'Manage company resources'),
              ('warehouse_manager', 'Manage shipments and drivers'),
              ('driver', 'View and update assigned deliveries'),
              ('customer', 'Track shipments via tracking number')
            ON CONFLICT (name) DO NOTHING
        """))

    # Start background simulation engine
    sim_task = asyncio.create_task(simulation_loop())
    logger.info("DropAI platform started — simulation engine running")
    yield
    sim_task.cancel()
    try:
        await sim_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()
    logger.info("DropAI platform shutdown complete")


app = FastAPI(
    title="DropAI API",
    description="Intelligent Delivery & Logistics Optimization Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for demo — restrict to ALLOWED_ORIGINS in production
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,          prefix="/api/v1/auth",          tags=["Authentication"])
app.include_router(companies.router,     prefix="/api/v1/companies",     tags=["Companies"])
app.include_router(users.router,         prefix="/api/v1/users",         tags=["Users"])
app.include_router(shipments.router,     prefix="/api/v1/shipments",     tags=["Shipments"])
app.include_router(drivers.router,       prefix="/api/v1/drivers",       tags=["Drivers"])
app.include_router(warehouses.router,    prefix="/api/v1/warehouses",    tags=["Warehouses"])
app.include_router(dashboard.router,     prefix="/api/v1/dashboard",     tags=["Dashboard"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "DropAI API", "version": settings.APP_VERSION}
