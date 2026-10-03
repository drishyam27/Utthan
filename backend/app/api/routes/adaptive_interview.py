"""
Utthan Backend - Adaptive Beneficiary Interview & Structured Profile Routes.
Phase 3B: Catalog-Aware Adaptive Interview State Machine & NSQF Competency Evidence.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from pydantic import BaseModel, Field
from supabase import Client

from app.db.supabase import get_supabase_client
from app.schemas.adaptive_interview import (
    AdaptiveAnswerSubmit,
    AdaptiveInterviewState,
    ProfileFieldCorrectionRequest,
    StructuredBeneficiaryProfile,
)
from app.schemas.nsqf_recommendation import NSQFRecommendationResponse
from app.schemas.groq_extraction import (
    ExplainRecommendationsRequest,
    ExplainRecommendationsResponse,
    InterpretTranscriptRequest,
    InterpretTranscriptResponse,
)

from app.schemas.beneficiary import LanguageCode
from app.schemas.common import ErrorResponse
from app.schemas.interview import InterviewCreateRequest
from app.services.adaptive_interview_service import (
    complete_adaptive_session,
    get_adaptive_interview_state,
    get_or_initialize_profile,
    submit_answer_to_interview,
    update_profile_field,
)
from app.services.groq_service import interpret_and_apply_to_session
from app.services.beneficiary_service import (
    CapabilityContext,
    CapabilityDeniedError,
    CapabilityTargetMismatchError,
    require_capability,
    require_matching_capability,
)
from app.services.interview_service import create_or_resume_interview

router = APIRouter(prefix="/adaptive-interview", tags=["Adaptive Interview"])
logger = logging.getLogger("utthan.adaptive_interview.routes")


class AdaptiveSessionStartRequest(BaseModel):
    beneficiary_id: UUID = Field(..., description="Target beneficiary UUID")
    language: LanguageCode = Field(default="hi", description="Interview language code")


def _get_optional_capability(
    authorization: Optional[str] = Header(default=None),
    client: Client = Depends(get_supabase_client),
) -> Optional[CapabilityContext]:
    if not authorization:
        return None
    try:
        return require_capability(client, authorization)
    except CapabilityDeniedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid beneficiary capability is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        logger.exception("Capability resolution failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable.",
        )


def _resolve_interview_and_beneficiary(
    interview_id: UUID,
    client: Client,
    capability: Optional[CapabilityContext],
) -> tuple[dict, UUID]:
    """Retrieves the interview row and asserts ownership if capability is present."""
    res = (
        client.table("interview_sessions")
        .select("*")
        .eq("id", str(interview_id))
        .limit(1)
        .execute()
    )
    rows = getattr(res, "data", [])
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {interview_id} not found.",
        )
    interview_row = rows[0]
    beneficiary_id = UUID(str(interview_row["beneficiary_id"]))

    if capability and capability.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This capability does not authorize access to this interview.",
        )

    return interview_row, beneficiary_id


@router.post(
    "/sessions",
    response_model=AdaptiveInterviewState,
    status_code=status.HTTP_201_CREATED,
    summary="Start or resume an adaptive interview session",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid capability"},
        403: {"model": ErrorResponse, "description": "Mismatched capability"},
        404: {"model": ErrorResponse, "description": "Beneficiary not found"},
    },
)
def start_or_resume_session(
    payload: AdaptiveSessionStartRequest,
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Initializes or resumes an adaptive interview session for a beneficiary,
    returning the active state with the next deterministic question.
    """
    if capability and capability.beneficiary_id != payload.beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This capability cannot access the requested beneficiary.",
        )

    try:
        session_contract = create_or_resume_interview(
            client,
            payload.beneficiary_id,
            InterviewCreateRequest(language=payload.language),
        )
        return get_adaptive_interview_state(client, session_contract.id, payload.beneficiary_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to start/resume adaptive session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize adaptive interview: {str(exc)}",
        )


@router.get(
    "/{interview_id}/state",
    response_model=AdaptiveInterviewState,
    summary="Get current adaptive interview state",
    responses={
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
def get_interview_state(
    interview_id: UUID = Path(...),
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Fetches the current progress, active question, and profile summary.
    """
    _, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    try:
        return get_adaptive_interview_state(client, interview_id, beneficiary_id)
    except Exception as exc:
        logger.exception("Failed to get interview state")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch interview state: {str(exc)}",
        )


@router.post(
    "/{interview_id}/answer",
    response_model=AdaptiveInterviewState,
    summary="Submit an answer and get next adaptive question",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid submission"},
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
def submit_answer(
    interview_id: UUID = Path(...),
    submission: AdaptiveAnswerSubmit = ...,
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Submits an answer (from manual option or voice transcript), updates the structured profile
    and NSQF competency evidence, and computes the next best question.
    """
    _, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    try:
        return submit_answer_to_interview(client, interview_id, beneficiary_id, submission)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to submit adaptive answer")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record answer: {str(exc)}",
        )


@router.post(
    "/{interview_id}/interpret",
    response_model=InterpretTranscriptResponse,
    summary="Interpret voice transcript or conversational text with Groq LLM",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid submission"},
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
async def interpret_transcript(
    interview_id: UUID = Path(...),
    payload: InterpretTranscriptRequest = ...,
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Interprets natural-language transcript (voice/text) with Groq LLM assistance,
    evaluates contradictions, detects ambiguity/clarification needs, and updates the profile.
    """
    _, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    try:
        return await interpret_and_apply_to_session(
            client=client,
            interview_id=interview_id,
            beneficiary_id=beneficiary_id,
            transcript=payload.transcript,
            lang=payload.language,
            question_id=payload.question_id,
            apply_to_profile=payload.apply_to_profile,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to interpret transcript with Groq")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to interpret dialogue: {str(exc)}",
        )


@router.get(
    "/{interview_id}/profile",
    response_model=StructuredBeneficiaryProfile,
    summary="Get current structured beneficiary profile",
    responses={
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
def get_profile(
    interview_id: UUID = Path(...),
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Retrieves the complete structured profile generated so far from the interview.
    """
    interview_row, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    b_res = client.table("beneficiaries").select("*").eq("id", str(beneficiary_id)).limit(1).execute()
    b_rows = getattr(b_res, "data", [])
    b_row = b_rows[0] if b_rows else {}
    return get_or_initialize_profile(interview_row, b_row)


@router.patch(
    "/{interview_id}/profile",
    response_model=StructuredBeneficiaryProfile,
    summary="Correct or update a structured profile field during review",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid field or value"},
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
def correct_field(
    interview_id: UUID = Path(...),
    payload: ProfileFieldCorrectionRequest = ...,
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Allows the citizen or field worker to correct an erroneous field during the review stage.
    """
    _, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    try:
        return update_profile_field(
            client,
            interview_id,
            beneficiary_id,
            payload.field_name,
            payload.value,
        )
    except Exception as exc:
        logger.exception("Failed to update profile field")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile field: {str(exc)}",
        )


@router.post(
    "/{interview_id}/complete",
    response_model=AdaptiveInterviewState,
    summary="Finalize and lock the adaptive interview session",
    responses={
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
def complete_interview(
    interview_id: UUID = Path(...),
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Marks the interview completed, finalizes the structured profile, and ensures
    all backward-compatible fields are populated for the recommendation engine.
    """
    _, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    try:
        return complete_adaptive_session(client, interview_id, beneficiary_id)
    except Exception as exc:
        logger.exception("Failed to complete adaptive interview")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete interview: {str(exc)}",
        )


@router.get(
    "/{interview_id}/recommendations",
    response_model=NSQFRecommendationResponse,
    summary="Get authoritative NSQF/NQR course recommendations for this interview",
    responses={
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
def get_interview_recommendations(
    interview_id: UUID = Path(...),
    limit: int = 15,
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Computes deterministic, explainable recommendations directly from the authoritative
    2,810-course NSQF/NQR catalog using the interview session's structured profile.
    """
    interview_row, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    from app.services.nsqf_recommendation_service import generate_nsqf_recommendations_for_beneficiary
    return generate_nsqf_recommendations_for_beneficiary(
        client=client,
        beneficiary_id=beneficiary_id,
        interview_id=interview_id,
        limit=limit,
    )


@router.post(
    "/{interview_id}/explain-recommendations",
    response_model=ExplainRecommendationsResponse,
    summary="Get conversational spoken explanation of deterministic NSQF recommendations",
    responses={
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
)
async def explain_interview_recommendations(
    interview_id: UUID = Path(...),
    payload: ExplainRecommendationsRequest = ExplainRecommendationsRequest(),
    capability: Optional[CapabilityContext] = Depends(_get_optional_capability),
    client: Client = Depends(get_supabase_client),
):
    """
    Invokes Groq to generate a natural conversational spoken explanation of
    deterministic NSQF recommendations. Groq receives the real recommendations
    and explains their deterministic match reasons faithfully without fabricating courses.
    """
    interview_row, beneficiary_id = _resolve_interview_and_beneficiary(interview_id, client, capability)
    from app.services.nsqf_recommendation_service import generate_nsqf_recommendations_for_beneficiary
    from app.services.groq_service import explain_nsqf_recommendations_with_groq

    b_res = client.table("beneficiaries").select("*").eq("id", str(beneficiary_id)).limit(1).execute()
    b_rows = getattr(b_res, "data", [])
    b_row = b_rows[0] if b_rows else {}
    profile = get_or_initialize_profile(interview_row, b_row)

    recs_response = generate_nsqf_recommendations_for_beneficiary(
        client=client,
        beneficiary_id=beneficiary_id,
        interview_id=interview_id,
        limit=payload.top_n,
    )

    lang = payload.language or profile.preferred_language or "hi"
    return await explain_nsqf_recommendations_with_groq(
        beneficiary_id=beneficiary_id,
        interview_id=interview_id,
        recommendations_response=recs_response,
        profile=profile,
        lang=lang,
        top_n=payload.top_n,
    )


