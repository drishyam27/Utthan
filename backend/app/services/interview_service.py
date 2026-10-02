"""Persistent draft and completion operations for anonymous interviews."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from supabase import Client

from app.schemas.interview import (
    InterviewCompletionRequest,
    InterviewCreateRequest,
    InterviewDraftUpdateRequest,
    InterviewResponsesContract,
    InterviewSessionContract,
)


INTERVIEW_COLUMNS = (
    "id, beneficiary_id, language, status, responses, extracted_profile, "
    "revision, created_at, updated_at, completed_at"
)


class InterviewNotFoundError(LookupError):
    """Raised when an interview is missing or not owned by the capability."""


class InterviewValidationError(ValueError):
    """Raised when persisted interview data cannot satisfy the contract."""


class InterviewConflictError(RuntimeError):
    """Raised when an optimistic-concurrency revision is stale."""


class InterviewAlreadyCompletedError(RuntimeError):
    """Raised when a completed interview is being changed or completed again."""


def _rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    return data if isinstance(data, list) else []


def _first(response: Any) -> Optional[dict[str, Any]]:
    rows = _rows(response)
    return rows[0] if rows else None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _responses_from_row(row: dict[str, Any]) -> dict[str, Any]:
    raw_responses = row.get("responses")
    if not isinstance(raw_responses, dict):
        raise InterviewValidationError("Interview responses must be an object.")
    try:
        responses = InterviewResponsesContract.model_validate(raw_responses)
    except Exception as exc:
        raise InterviewValidationError("Interview responses do not match the supported contract.") from exc
    return responses.model_dump(exclude_none=True)


def _contract_from_row(row: dict[str, Any]) -> InterviewSessionContract:
    normalized = dict(row)
    normalized["responses"] = _responses_from_row(row)
    try:
        return InterviewSessionContract(**normalized)
    except Exception as exc:
        raise InterviewValidationError("Interview session data is invalid.") from exc


def _owned_interview(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
) -> Optional[dict[str, Any]]:
    response = (
        client.table("interview_sessions")
        .select(INTERVIEW_COLUMNS)
        .eq("id", str(interview_id))
        .eq("beneficiary_id", str(beneficiary_id))
        .limit(1)
        .execute()
    )
    return _first(response)


def _latest_interview(
    client: Client,
    beneficiary_id: UUID,
) -> Optional[dict[str, Any]]:
    response = (
        client.table("interview_sessions")
        .select(INTERVIEW_COLUMNS)
        .eq("beneficiary_id", str(beneficiary_id))
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return _first(response)


def create_or_resume_interview(
    client: Client,
    beneficiary_id: UUID,
    payload: InterviewCreateRequest,
) -> InterviewSessionContract:
    """Return the latest session, or create one draft for this beneficiary.

    A beneficiary has one deterministic current interview for this phase. This
    makes refreshes, retries, and repeated initialization resume the existing
    draft; a completed session is returned as completed and never reopened.
    """

    existing = _latest_interview(client, beneficiary_id)
    if existing:
        return _contract_from_row(existing)

    now = _now().isoformat()
    inserted = (
        client.table("interview_sessions")
        .insert(
            {
                "beneficiary_id": str(beneficiary_id),
                "language": payload.language,
                "status": "draft",
                "responses": {},
                "revision": 1,
                "updated_at": now,
                "completed_at": None,
                "extracted_profile": None,
            }
        )
        .select(INTERVIEW_COLUMNS)
        .execute()
    )
    row = _first(inserted)
    if not row:
        raise RuntimeError("interview insert returned no record")
    return _contract_from_row(row)


def get_interview(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
) -> InterviewSessionContract:
    row = _owned_interview(client, interview_id, beneficiary_id)
    if not row:
        raise InterviewNotFoundError
    return _contract_from_row(row)


def _classify_failed_update(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
    expected_revision: int,
) -> None:
    current = _owned_interview(client, interview_id, beneficiary_id)
    if not current:
        raise InterviewNotFoundError
    if current.get("status") == "completed":
        raise InterviewAlreadyCompletedError
    if current.get("revision") != expected_revision:
        raise InterviewConflictError
    raise InterviewConflictError


def update_draft_interview(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
    payload: InterviewDraftUpdateRequest,
) -> InterviewSessionContract:
    current = get_interview(client, interview_id, beneficiary_id)
    if current.status == "completed":
        raise InterviewAlreadyCompletedError
    if current.revision != payload.expected_revision:
        raise InterviewConflictError

    responses = payload.responses.model_dump(exclude_none=True)
    update = (
        client.table("interview_sessions")
        .update(
            {
                "responses": responses,
                "revision": payload.expected_revision + 1,
                "updated_at": _now().isoformat(),
            }
        )
        .eq("id", str(interview_id))
        .eq("beneficiary_id", str(beneficiary_id))
        .eq("status", "draft")
        .eq("revision", payload.expected_revision)
        .select(INTERVIEW_COLUMNS)
        .execute()
    )
    row = _first(update)
    if not row:
        _classify_failed_update(client, interview_id, beneficiary_id, payload.expected_revision)
    return _contract_from_row(row)


def complete_interview(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
    payload: InterviewCompletionRequest,
) -> InterviewSessionContract:
    current = get_interview(client, interview_id, beneficiary_id)
    if current.status == "completed":
        raise InterviewAlreadyCompletedError
    if current.revision != payload.expected_revision:
        raise InterviewConflictError

    responses = InterviewResponsesContract.model_validate(current.responses)
    if not responses.required_fields_present():
        raise InterviewValidationError("All four interview answers are required before completion.")

    completed_at = _now().isoformat()
    update = (
        client.table("interview_sessions")
        .update(
            {
                "status": "completed",
                "completed_at": completed_at,
                "updated_at": completed_at,
                "revision": payload.expected_revision + 1,
            }
        )
        .eq("id", str(interview_id))
        .eq("beneficiary_id", str(beneficiary_id))
        .eq("status", "draft")
        .eq("revision", payload.expected_revision)
        .select(INTERVIEW_COLUMNS)
        .execute()
    )
    row = _first(update)
    if not row:
        _classify_failed_update(client, interview_id, beneficiary_id, payload.expected_revision)
    return _contract_from_row(row)
