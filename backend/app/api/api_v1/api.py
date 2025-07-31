"""
Main API Router
Combines all API endpoints for version 1

Developed by: Qryti Dev Team
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, organizations, assessments, stages, evidence, reports

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(stages.router, prefix="/stages", tags=["stages"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

