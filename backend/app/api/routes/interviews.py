"""Capability-protected persistent interview lifecycle routes."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from supabase import Client

from app.db.supabase import get_supabase_client
from app.schemas.common import ErrorResponse
from app.schemas.interview import (
    InterviewCompletionRequest,
    InterviewCreateRequest,
    InterviewDraftUpdateRequest,
    InterviewSessionContract,
)
from app.services.beneficiary_service import (
    CapabilityContext,
    CapabilityDeniedError,
    CapabilityTargetMismatchError,
    require_capability,
    require_matching_capability,
)
from app.services.interview_service import (
    InterviewAlreadyCompletedError,
    InterviewConflictError,
    InterviewNotFoundError,
    InterviewValidationError,
    complete_interview,
    create_or_resume_interview,
    get_interview,
    update_draft_interview,
)


router = APIRouter(tags=["Interviews"])
logger = logging.getLogger(__name__)


def _interview_capability_dependency(
    authorization: Optional[str] = Header(default=None),
    client: Client = Depends(get_supabase_client),
) -> CapabilityContext:
    try:
        return require_capability(client, authorization)
    except CapabilityDeniedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid beneficiary capability is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        logger.exception("Interview capability lookup failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interview service is temporarily unavailable.",
        )


def _beneficiary_interview_capability_dependency(
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
        logger.exception("Beneficiary interview capability lookup failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interview service is temporarily unavailable.",
        )


def _raise_service_error(exc: Exception) -> None:
    if isinstance(exc, InterviewNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found.",
        )
    if isinstance(exc, InterviewValidationError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    if isinstance(exc, InterviewConflictError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The interview changed since it was loaded. Please refresh and try again.",
        )
    if isinstance(exc, InterviewAlreadyCompletedError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This interview has already been completed.",
        )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Interview service is temporarily unavailable.",
    )


@router.post(
    "/beneficiaries/{beneficiary_id}/interviews",
    response_model=InterviewSessionContract,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        403: {"model": ErrorResponse, "description": "Capability does not authorize beneficiary"},
        503: {"model": ErrorResponse, "description": "Interview service unavailable"},
    },
    summary="Create or resume the current beneficiary interview",
)
def create_or_resume(
    beneficiary_id: UUID,
    payload: InterviewCreateRequest,
    capability: CapabilityContext = Depends(_beneficiary_interview_capability_dependency),
    client: Client = Depends(get_supabase_client),
):
    try:
        return create_or_resume_interview(client, capability.beneficiary_id, payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Interview creation/resume failed")
        _raise_service_error(exc)


@router.get(
    "/interviews/{interview_id}",
    response_model=InterviewSessionContract,
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        404: {"model": ErrorResponse, "description": "Interview not found"},
    },
    summary="Get an authorized interview session",
)
def get_session(
    interview_id: UUID,
    capability: CapabilityContext = Depends(_interview_capability_dependency),
    client: Client = Depends(get_supabase_client),
):
    try:
        return get_interview(client, interview_id, capability.beneficiary_id)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Interview retrieval failed")
        _raise_service_error(exc)


@router.patch(
    "/interviews/{interview_id}",
    response_model=InterviewSessionContract,
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        404: {"model": ErrorResponse, "description": "Interview not found"},
        409: {"model": ErrorResponse, "description": "Stale revision or completed interview"},
        422: {"model": ErrorResponse, "description": "Invalid interview responses"},
    },
    summary="Update a draft interview",
)
def patch_session(
    interview_id: UUID,
    payload: InterviewDraftUpdateRequest,
    capability: CapabilityContext = Depends(_interview_capability_dependency),
    client: Client = Depends(get_supabase_client),
):
    try:
        return update_draft_interview(client, interview_id, capability.beneficiary_id, payload)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Interview draft update failed")
        _raise_service_error(exc)


@router.post(
    "/interviews/{interview_id}/complete",
    response_model=InterviewSessionContract,
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        404: {"model": ErrorResponse, "description": "Interview not found"},
        409: {"model": ErrorResponse, "description": "Stale revision or completed interview"},
        422: {"model": ErrorResponse, "description": "Incomplete interview responses"},
    },
    summary="Complete a draft interview",
)
def complete_session(
    interview_id: UUID,
    payload: InterviewCompletionRequest,
    capability: CapabilityContext = Depends(_interview_capability_dependency),
    client: Client = Depends(get_supabase_client),
):
    try:
        return complete_interview(client, interview_id, capability.beneficiary_id, payload)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Interview completion failed")
        _raise_service_error(exc)
