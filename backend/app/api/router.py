"""
API Router - Aggregates all API v1 routes
"""

from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    auth,
    dependencies_api,
    optimization,
    price_decks,
    projects,
    reports,
    scenarios,
)

# Create main API router
api_router = APIRouter()

# Create v1 router
v1_router = APIRouter(prefix="/v1")

# Include all v1 sub-routers
v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

v1_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"],
)

v1_router.include_router(
    scenarios.router,
    prefix="/scenarios",
    tags=["scenarios"],
)

v1_router.include_router(
    optimization.router,
    prefix="/optimization",
    tags=["optimization"],
)

v1_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
)

v1_router.include_router(
    dependencies_api.router,
    prefix="/dependencies",
    tags=["dependencies"],
)

v1_router.include_router(
    price_decks.router,
    prefix="/price-decks",
    tags=["price-decks"],
)

v1_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["reports"],
)

# Include v1 router in main API router
api_router.include_router(v1_router)
