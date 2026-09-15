"""Typed deterministic recommendation response contracts."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RecommendationSkillMetadata(BaseModel):
    id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=150)
    sector: Optional[str] = None
    nsqf_level: Optional[int] = Field(None, ge=1, le=8)
    qp_code: Optional[str] = None
    is_taught: Optional[bool] = None


class RecommendationResultContract(BaseModel):
    opportunity_id: str = Field(..., min_length=1, max_length=64)
    eligible: bool
    score: int = Field(..., ge=0, le=100)
    matched_criteria: List[str] = Field(default_factory=list)
    unmet_criteria: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    nsqf_level: Optional[int] = Field(None, ge=1, le=8)
    qp_code: Optional[str] = None
    skills: List[RecommendationSkillMetadata] = Field(default_factory=list)


class RecommendationResponseContract(BaseModel):
    beneficiary_id: UUID
    state_id: Optional[str] = None
    district_id: Optional[str] = None
    generated_at: datetime
    recommendations: List[RecommendationResultContract] = Field(default_factory=list)
