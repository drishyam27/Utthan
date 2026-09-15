"""
Location Master API Routes.
Queries authoritative Government of India State and District data from Supabase.
"""

from typing import List
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from supabase import Client
from app.db.supabase import get_supabase_client
from app.schemas.location import (
    StateResponse,
    StateDistrictsResponse,
    DistrictResponse,
    LocationResolveRequest,
    ResolvedLocationResponse,
)
from app.schemas.common import ErrorResponse
from app.services.location_resolution import (
    AmbiguousLocationError,
    LocationProviderError,
    LocationResolutionError,
    LocationResolver,
    get_reverse_geocoder,
)

router = APIRouter(prefix="/locations", tags=["Locations"])
logger = logging.getLogger(__name__)


@router.post(
    "/resolve",
    response_model=ResolvedLocationResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Location could not be mapped to one canonical LGD district"},
        503: {"model": ErrorResponse, "description": "Location provider unavailable"},
    },
    summary="Resolve browser coordinates to canonical LGD location",
    description=(
        "Reverse-resolves transient browser coordinates and validates the result "
        "against the authoritative Supabase LGD state and district master."
    ),
)
def resolve_location(
    payload: LocationResolveRequest,
    client: Client = Depends(get_supabase_client),
    geocoder=Depends(get_reverse_geocoder),
):
    try:
        resolver = LocationResolver(client=client, geocoder=geocoder)
        return resolver.resolve(
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except LocationProviderError:
        logger.warning("Location resolution provider unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Location service is temporarily unavailable. Please try again.",
        )
    except (LocationResolutionError, AmbiguousLocationError):
        logger.info("Location could not be mapped to one canonical LGD district")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="We could not confirm one official State and District for this location.",
        )


@router.get(
    "/states",
    response_model=List[StateResponse],
    summary="List all States and Union Territories",
    description="Returns all 36 Indian States and Union Territories from the authoritative location master."
)
def list_states(client: Client = Depends(get_supabase_client)):
    try:
        response = client.table("states").select("id, code, name, type, lgd_code").order("name").execute()
        return [StateResponse(**row) for row in (response.data or [])]
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to retrieve states from Supabase")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve states from the database."
        )


@router.get(
    "/states/{state_code}/districts",
    response_model=StateDistrictsResponse,
    responses={404: {"model": ErrorResponse, "description": "State not found"}},
    summary="List districts for a specific State/UT",
    description="Returns all official LGD districts belonging to the given state code (e.g. 'UP' or 'state-up')."
)
def list_districts_by_state(state_code: str, client: Client = Depends(get_supabase_client)):
    try:
        normalized_code = state_code.strip()
        # Find the state by code (e.g. 'UP') or id (e.g. 'state-up')
        state_query = client.table("states").select("id, code, name, type, lgd_code")
        
        if normalized_code.startswith("state-") or normalized_code.startswith("ut-"):
            state_res = state_query.eq("id", normalized_code).execute()
        else:
            state_res = state_query.ilike("code", normalized_code).execute()

        if not state_res.data or len(state_res.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"State with identifier or code '{state_code}' was not found in location master."
            )

        state_data = state_res.data[0]
        state_id = state_data["id"]

        # Fetch districts for this state
        dist_res = client.table("districts").select(
            "id, name, code, state_id, lgd_district_code"
        ).eq("state_id", state_id).order("name").execute()

        districts = [DistrictResponse(**row) for row in (dist_res.data or [])]

        return StateDistrictsResponse(
            state=StateResponse(**state_data),
            total_districts=len(districts),
            districts=districts
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to retrieve districts for state identifier")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve districts from the database."
        )
