"""Capability-protected deterministic recommendation API routes."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from supabase import Client

from app.db.supabase import get_supabase_client
from app.schemas.common import ErrorResponse
from app.schemas.nsqf_recommendation import NSQFRecommendationResponse
from app.schemas.recommendation import RecommendationResponseContract
from app.services.beneficiary_service import (
    BeneficiaryNotFoundError,
    CapabilityContext,
    CapabilityDeniedError,
    CapabilityTargetMismatchError,
    require_matching_capability,
)
from app.services.nsqf_recommendation_service import generate_nsqf_recommendations_for_beneficiary
from app.services.recommendation_service import generate_recommendations

router = APIRouter(tags=["Recommendations"])
logger = logging.getLogger(__name__)


def _recommendation_capability_dependency(
    beneficiary_id: UUID = Path(...),
    authorization: Optional[str] = Header(default=None),
    client: Client = Depends(get_supabase_client),
) -> CapabilityContext:
    try:
        return require_matching_capability(client, authorization, beneficiary_id)
    except CapabilityTargetMismatchError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This capability cannot access the requested beneficiary.",
        )
    except CapabilityDeniedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid beneficiary capability is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        logger.exception("Recommendation capability lookup failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation service is temporarily unavailable.",
        )


@router.get(
    "/beneficiaries/{beneficiary_id}/recommendations",
    response_model=RecommendationResponseContract,
    summary="Get Deterministic Recommendations",
    description=(
        "Computes rule-based, NSQF-aligned opportunity matches from the beneficiary's "
        "persisted completed interview. Zero LLM hallucination."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        403: {"model": ErrorResponse, "description": "Capability does not authorize beneficiary"},
        404: {"model": ErrorResponse, "description": "Beneficiary not found"},
        503: {"model": ErrorResponse, "description": "Recommendation service unavailable"},
    },
)
def get_recommendations(
    beneficiary_id: UUID,
    capability: CapabilityContext = Depends(_recommendation_capability_dependency),
    client: Client = Depends(get_supabase_client),
):
    try:
        return generate_recommendations(client, capability.beneficiary_id)
    except BeneficiaryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beneficiary {beneficiary_id} was not found.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to generate recommendations for %s", beneficiary_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation service is temporarily unavailable.",
        )


@router.get(
    "/beneficiaries/{beneficiary_id}/recommendations/nsqf",
    response_model=NSQFRecommendationResponse,
    summary="Get Authoritative NSQF/NQR Catalog Recommendations (Engine 2.0)",
    description=(
        "Computes deterministic, explainable qualification matches directly from the "
        "authoritative 2,810-course NSQF/NQR catalog based on the beneficiary's structured "
        "Phase 3B profile and verified competency evidence. Zero LLM hallucination."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        403: {"model": ErrorResponse, "description": "Capability does not authorize beneficiary"},
        404: {"model": ErrorResponse, "description": "Beneficiary not found"},
        503: {"model": ErrorResponse, "description": "Recommendation service unavailable"},
    },
)
def get_nsqf_recommendations(
    beneficiary_id: UUID,
    interview_id: Optional[UUID] = None,
    limit: int = 15,
    capability: CapabilityContext = Depends(_recommendation_capability_dependency),
    client: Client = Depends(get_supabase_client),
):
    try:
        return generate_nsqf_recommendations_for_beneficiary(
            client=client,
            beneficiary_id=capability.beneficiary_id,
            interview_id=interview_id,
            limit=limit,
        )
    except BeneficiaryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beneficiary {beneficiary_id} was not found.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to generate NSQF recommendations for %s", beneficiary_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NSQF Recommendation service is temporarily unavailable.",
        )

