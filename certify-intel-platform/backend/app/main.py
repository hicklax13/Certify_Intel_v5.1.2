"""
Certify Intel Platform - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import competitors, evidence, claims, insights, alerts, health
from app.core.config import settings
from app.core.database import engine
from app.models import base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    # Note: In production, use Alembic migrations instead
    # async with engine.begin() as conn:
    #     await conn.run_sync(base.Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Certify Intel Platform",
    description="AI-powered competitive intelligence for Certify Health",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(competitors.router, prefix="/api/competitors", tags=["Competitors"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(claims.router, prefix="/api/claims", tags=["Claims"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Certify Intel Platform",
        "version": "1.0.0",
        "status": "operational",
    }
