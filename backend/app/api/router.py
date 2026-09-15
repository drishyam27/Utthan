"""
Central API Router for Utthan Backend.
Combines all sub-routers under the /api prefix.
"""

from fastapi import APIRouter
from app.api.routes import beneficiaries, health, locations, opportunities

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(locations.router)
api_router.include_router(opportunities.router)
api_router.include_router(beneficiaries.router)
