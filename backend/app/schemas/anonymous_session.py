"""Persisted anonymous capability-session contracts."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnonymousSessionRecord(BaseModel):
    """Server-side session metadata; raw capability tokens are never represented."""

    id: UUID
    beneficiary_id: UUID
    token_hash: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    expires_at: datetime
    created_at: datetime
    last_used_at: Optional[datetime] = None
    rotated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
