"""Anonymous beneficiary profile API routes."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from supabase import Client

from app.db.supabase import get_supabase_client
from app.schemas.beneficiary import (
    BeneficiaryCreateRequest,
    BeneficiaryCreateResponse,
    BeneficiaryProfileContract,
    BeneficiaryUpdateRequest,
)
from app.schemas.common import ErrorResponse
from app.services.beneficiary_service import (
    BeneficiaryNotFoundError,
    BeneficiaryValidationError,
    CapabilityDeniedError,
    CapabilityTargetMismatchError,
    create_beneficiary,
    get_beneficiary,
    require_matching_capability,
    update_beneficiary,
)


router = APIRouter(prefix="/beneficiaries", tags=["Beneficiaries"])
logger = logging.getLogger(__name__)


def _capability_dependency(
    beneficiary_id: UUID = Path(...),
    authorization: Optional[str] = Header(default=None),
    client: Client = Depends(get_supabase_client),
) -> None:
    try:
        require_matching_capability(client, authorization, beneficiary_id)
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
        logger.exception("Beneficiary capability lookup failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Beneficiary service is temporarily unavailable.",
        )


@router.post(
    "",
    response_model=BeneficiaryCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "Invalid beneficiary profile or location"},
        503: {"model": ErrorResponse, "description": "Beneficiary service unavailable"},
    },
    summary="Create an anonymous beneficiary profile",
)
def create_profile(
    payload: BeneficiaryCreateRequest,
    client: Client = Depends(get_supabase_client),
):
    try:
        beneficiary, raw_token = create_beneficiary(client, payload)
        return BeneficiaryCreateResponse(
            beneficiary=beneficiary,
            session_token=raw_token,
        )
    except BeneficiaryValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except HTTPException:
        raise
    except Exception:
        logger.exception("Beneficiary creation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beneficiary profile could not be created.",
        )


@router.get(
    "/{beneficiary_id}",
    response_model=BeneficiaryProfileContract,
    dependencies=[Depends(_capability_dependency)],
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        403: {"model": ErrorResponse, "description": "Capability does not authorize beneficiary"},
        404: {"model": ErrorResponse, "description": "Beneficiary not found"},
    },
    summary="Get an authorized beneficiary profile",
)
def get_profile(
    beneficiary_id: UUID,
    client: Client = Depends(get_supabase_client),
):
    try:
        return get_beneficiary(client, beneficiary_id)
    except BeneficiaryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary profile not found.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Beneficiary retrieval failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beneficiary profile could not be retrieved.",
        )


@router.patch(
    "/{beneficiary_id}",
    response_model=BeneficiaryProfileContract,
    dependencies=[Depends(_capability_dependency)],
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid capability"},
        403: {"model": ErrorResponse, "description": "Capability does not authorize beneficiary"},
        404: {"model": ErrorResponse, "description": "Beneficiary not found"},
        422: {"model": ErrorResponse, "description": "Invalid beneficiary profile or location"},
    },
    summary="Update an authorized beneficiary profile",
)
def patch_profile(
    beneficiary_id: UUID,
    payload: BeneficiaryUpdateRequest,
    client: Client = Depends(get_supabase_client),
):
    try:
        return update_beneficiary(client, beneficiary_id, payload)
    except BeneficiaryValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except BeneficiaryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary profile not found.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Beneficiary update failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beneficiary profile could not be updated.",
        )
