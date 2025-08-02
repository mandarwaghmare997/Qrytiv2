"""
API v1 Router
Main API router that includes all endpoint modules

Developed by: Qryti Dev Team
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, organizations

# Create API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"]
)

