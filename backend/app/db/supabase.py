"""
Utthan Backend - Supabase Client Layer
Provides an isolated, secure server-side connection to Supabase PostgreSQL.
Credentials are kept exclusively on the server and are never exposed to clients.
"""

from typing import Optional, Tuple
import logging
from fastapi import HTTPException, status
from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Optional[Client] = None
logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """
    Returns the singleton Supabase client instance.
    Raises HTTPException(503) with a helpful message if credentials are not configured.
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client

    if not settings.is_supabase_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Database service unconfigured. Please configure SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY in backend/.env to enable database access."
            )
        )

    try:
        _supabase_client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
        )
        return _supabase_client
    except Exception:
        logger.exception("Failed to initialize Supabase client")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to initialize the database service."
        )


def check_db_connection() -> Tuple[bool, str]:
    """
    Performs a lightweight query to verify active connectivity with Supabase.
    Returns (is_connected, message).
    """
    if not settings.is_supabase_configured:
        return False, "Supabase credentials are not configured in backend/.env"

    try:
        client = get_supabase_client()
        # Query states table with limit 1 as a lightweight heartbeat
        response = client.table("states").select("id").limit(1).execute()
        if response and hasattr(response, "data"):
            return True, "Database connection active and responsive"
        return False, "Unexpected empty response from database"
    except HTTPException as exc:
        return False, exc.detail
    except Exception as exc:
        err_str = str(exc).lower()
        if "permission denied" in err_str:
            logger.warning("Supabase database permission denied; apply the permissions migration")
            return False, "Database permission denied: run supabase/migrations/20260915000002_grant_permissions.sql in Supabase SQL editor"
        # Never leak raw connection strings, tokens or passwords
        logger.exception("Supabase database health check failed")
        return False, "Database connection failed or remote host unreachable"
