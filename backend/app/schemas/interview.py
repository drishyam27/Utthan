"""Typed interview lifecycle contracts for Phase 2C."""

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.beneficiary import LanguageCode


InterviewStatus = Literal["draft", "completed"]


class InterviewSessionContract(BaseModel):
    """Structured interview state; individual answers remain JSON data."""

    id: Optional[UUID] = None
    beneficiary_id: Optional[UUID] = None
    language: LanguageCode = "hi"
    status: InterviewStatus = "draft"
    responses: dict[str, Any] = Field(default_factory=dict)
    extracted_profile: Optional[dict[str, Any]] = None
    transcript_log: Optional[str] = None
    revision: int = Field(1, ge=1)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_completion_timestamp(self):
        if self.status == "completed" and self.completed_at is None:
            raise ValueError("completed interview sessions require completed_at")
        if self.status == "draft" and self.completed_at is not None:
            raise ValueError("draft interview sessions cannot have completed_at")
        return self
