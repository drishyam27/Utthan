"""Service-layer operations for anonymous beneficiary profiles."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from supabase import Client

from app.schemas.beneficiary import (
    BeneficiaryCreateRequest,
    BeneficiaryProfileContract,
    BeneficiaryUpdateRequest,
)
from app.security.anonymous_session import (
    generate_capability_token,
    hash_capability_token,
    verify_capability_token,
)


PROFILE_COLUMNS = (
    "id, name, preferred_language, state_id, district_id, education_level, "
    "current_occupation, mobility_preference, primary_goal"
)
SESSION_TTL = timedelta(days=30)


class BeneficiaryValidationError(ValueError):
    """Raised when a profile value is not valid for the canonical data model."""


class BeneficiaryNotFoundError(LookupError):
    """Raised when a beneficiary record does not exist."""


class CapabilityDeniedError(PermissionError):
    """Raised when a capability is missing, invalid, expired, or revoked."""


class CapabilityTargetMismatchError(CapabilityDeniedError):
    """Raised when a valid capability targets a different beneficiary."""


@dataclass(frozen=True)
class CapabilityContext:
    beneficiary_id: UUID


def _rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    return data if isinstance(data, list) else []


def _first(response: Any) -> Optional[dict[str, Any]]:
    rows = _rows(response)
    return rows[0] if rows else None


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def validate_canonical_location(client: Client, state_id: str, district_id: str) -> None:
    """Require an existing state and a district belonging to that state."""

    state_response = (
        client.table("states")
        .select("id")
        .eq("id", state_id)
        .limit(1)
        .execute()
    )
    if not _first(state_response):
        raise BeneficiaryValidationError("The selected State is not valid.")

    district_response = (
        client.table("districts")
        .select("id, state_id")
        .eq("id", district_id)
        .eq("state_id", state_id)
        .limit(1)
        .execute()
    )
    if not _first(district_response):
        raise BeneficiaryValidationError("The selected District is not valid for the selected State.")


def _profile_from_row(row: dict[str, Any]) -> BeneficiaryProfileContract:
    return BeneficiaryProfileContract(**row)


def create_beneficiary(
    client: Client,
    payload: BeneficiaryCreateRequest,
) -> tuple[BeneficiaryProfileContract, str]:
    validate_canonical_location(client, payload.state_id, payload.district_id)

    inserted = (
        client.table("beneficiaries")
        .insert(payload.model_dump())
        .select(PROFILE_COLUMNS)
        .execute()
    )
    row = _first(inserted)
    if not row or not row.get("id"):
        raise RuntimeError("beneficiary insert returned no record")

    beneficiary_id = str(row["id"])
    raw_token = generate_capability_token()
    expires_at = _now() + SESSION_TTL
    try:
        session_insert = (
            client.table("beneficiary_sessions")
            .insert(
                {
                    "beneficiary_id": beneficiary_id,
                    "token_hash": hash_capability_token(raw_token),
                    "expires_at": expires_at.isoformat(),
                }
            )
            .select("id")
            .execute()
        )
        if not _first(session_insert):
            raise RuntimeError("beneficiary session insert returned no record")
    except Exception:
        try:
            client.table("beneficiaries").delete().eq("id", beneficiary_id).execute()
        except Exception:
            # Do not replace the original safe error with cleanup details.
            pass
        raise

    return _profile_from_row(row), raw_token


def get_beneficiary(client: Client, beneficiary_id: UUID) -> BeneficiaryProfileContract:
    response = (
        client.table("beneficiaries")
        .select(PROFILE_COLUMNS)
        .eq("id", str(beneficiary_id))
        .limit(1)
        .execute()
    )
    row = _first(response)
    if not row:
        raise BeneficiaryNotFoundError
    return _profile_from_row(row)


def update_beneficiary(
    client: Client,
    beneficiary_id: UUID,
    payload: BeneficiaryUpdateRequest,
) -> BeneficiaryProfileContract:
    existing = get_beneficiary(client, beneficiary_id)
    updates = payload.model_dump(exclude_unset=True)

    if "state_id" in updates or "district_id" in updates:
        state_id = updates.get("state_id", existing.state_id)
        district_id = updates.get("district_id", existing.district_id)
        if not state_id or not district_id:
            raise BeneficiaryValidationError(
                "State and District must be provided together as canonical identifiers."
            )
        validate_canonical_location(client, state_id, district_id)

    updates["updated_at"] = _now().isoformat()
    response = (
        client.table("beneficiaries")
        .update(updates)
        .eq("id", str(beneficiary_id))
        .select(PROFILE_COLUMNS)
        .execute()
    )
    row = _first(response)
    if not row:
        raise BeneficiaryNotFoundError
    return _profile_from_row(row)


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not isinstance(authorization, str):
        return None
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token or len(token) > 512:
        return None
    return token.strip() or None


def require_capability(
    client: Client,
    authorization: Optional[str],
) -> CapabilityContext:
    raw_token = _extract_bearer_token(authorization)
    if not raw_token:
        raise CapabilityDeniedError

    token_hash = hash_capability_token(raw_token)
    response = (
        client.table("beneficiary_sessions")
        .select("beneficiary_id, expires_at, revoked_at")
        .eq("token_hash", token_hash)
        .limit(1)
        .execute()
    )
    session = _first(response)
    if not session or session.get("revoked_at"):
        raise CapabilityDeniedError

    expires_at = _parse_timestamp(session.get("expires_at"))
    if not expires_at or expires_at <= _now():
        raise CapabilityDeniedError

    try:
        beneficiary_id = UUID(str(session["beneficiary_id"]))
    except (KeyError, ValueError):
        raise CapabilityDeniedError

    # The existing schema explicitly provides last_used_at; do not extend expiry.
    client.table("beneficiary_sessions").update(
        {"last_used_at": _now().isoformat()}
    ).eq("token_hash", token_hash).execute()

    if not verify_capability_token(raw_token, token_hash):
        raise CapabilityDeniedError
    return CapabilityContext(beneficiary_id=beneficiary_id)


def require_matching_capability(
    client: Client,
    authorization: Optional[str],
    beneficiary_id: UUID,
) -> CapabilityContext:
    context = require_capability(client, authorization)
    if context.beneficiary_id != beneficiary_id:
        raise CapabilityTargetMismatchError
    return context
