"""
Health Check API Routes.
Provides basic service heartbeat and optional database connectivity status.
"""

from fastapi import APIRouter, Response, status
from app.core.config import settings
from app.schemas.common import HealthResponse, DBHealthResponse
from app.db.supabase import check_db_connection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Application Health Heartbeat",
    description="Returns standard operational status of the Utthan backend service without database dependency."
)
def get_health():
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT
    )


@router.get(
    "/db",
    response_model=DBHealthResponse,
    summary="Database Connectivity Health Check",
    description="Tests connectivity with the remote Supabase PostgreSQL database."
)
def get_db_health(response: Response):
    is_connected, message = check_db_connection()
    if not is_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return DBHealthResponse(
            status="error",
            database="disconnected",
            message=message
        )
    return DBHealthResponse(
        status="ok",
        database="connected",
        message=message
    )
