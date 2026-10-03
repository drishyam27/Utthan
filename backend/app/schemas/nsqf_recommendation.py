"""
Utthan Backend - Pydantic Schemas for NSQF Recommendation Engine 2.0.
Authoritative NSQF/NQR Catalog Recommendations with Deterministic Eligibility and Explainable Ranking.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NSQFEligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    INSUFFICIENT_PROFILE = "insufficient_profile"
    REQUIREMENT_UNAVAILABLE = "requirement_unavailable"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class NSQFEligibilityEvaluation(BaseModel):
    """Structured evaluation of a candidate against a qualification's requirements."""
    status: NSQFEligibilityStatus = Field(..., description="Deterministic eligibility status")
    eligible: bool = Field(..., description="True if candidate passes all active hard gates")
    hard_failures: List[str] = Field(default_factory=list, description="Reasons for hard rejection")
    warnings: List[str] = Field(default_factory=list, description="Advisories or caveats")
    matched_requirements: List[str] = Field(default_factory=list, description="Explicitly satisfied requirements")
    unavailable_requirements: List[str] = Field(
        default_factory=list,
        description="Requirements not recorded in catalog metadata that cannot be evaluated"
    )


class NSQFRecommendationItem(BaseModel):
    """An authoritative course recommended from nsqf_qualifications."""
    model_config = ConfigDict(extra="ignore")

    q_code: str = Field(..., description="Official NQR qualification code (e.g. '2022/AA/AASSC/06397')")
    title: str = Field(..., description="Official qualification title")
    sector_id: str = Field(..., description="Slugified sector ID")
    sector_name: str = Field(..., description="Official NSQF sector name")
    nsqf_level: float = Field(..., description="Official NSQF level, preserving decimal half-levels (e.g. 2.5, 4.5)")
    qualification_type: Optional[str] = Field(None, description="e.g. 'General Qualification', 'NTC', 'Apprenticeship'")
    notional_hours_range: Optional[str] = Field(None, description="Official bucket, e.g. '401–600'")
    min_notional_hours: Optional[int] = Field(None, description="Minimum training hours")
    max_notional_hours: Optional[int] = Field(None, description="Maximum training hours")
    is_pwd: bool = Field(default=False, description="Whether qualification has PwD accessibility/tailoring")
    pwd_categories: List[str] = Field(default_factory=list, description="Specific PwD categories (VI, SHI, LD, ID)")
    awarding_body: Optional[str] = Field(None, description="Official awarding sector skill council or agency")
    proposed_occupation: Optional[str] = Field(None, description="Target job roles / occupations")
    progression_pathway: Optional[str] = Field(None, description="Vertical and horizontal career progression")
    description: Optional[str] = Field(None, description="Curriculum and role description")
    
    # Deterministic Scoring & Ranking
    score: int = Field(..., ge=0, le=100, description="Deterministic match score (0-100)")
    rank: int = Field(..., ge=1, description="Deterministic rank position")
    eligibility: NSQFEligibilityEvaluation = Field(..., description="Full eligibility evaluation details")
    match_reasons: List[str] = Field(default_factory=list, description="Explainable, human-readable match reasons")
    warnings: List[str] = Field(default_factory=list, description="Any caveats or missing catalog info warnings")
    source: Literal["nsqf_nqr_catalog"] = "nsqf_nqr_catalog"


class NSQFRecommendationResponse(BaseModel):
    """Full API response for authoritative NSQF catalog recommendations."""
    beneficiary_id: UUID
    interview_id: Optional[UUID] = None
    status: str = Field(..., description="'eligible', 'insufficient_profile', or 'no_match'")
    generated_at: datetime
    total_evaluated: int = Field(..., description="Total catalog courses considered")
    total_recommended: int = Field(..., description="Total courses passing eligibility")
    missing_profile_fields: List[str] = Field(
        default_factory=list,
        description="Fields required to make recommendations if profile is insufficient"
    )
    recommendations: List[NSQFRecommendationItem] = Field(
        default_factory=list,
        description="Ranked authoritative recommendations from nsqf_qualifications"
    )
    ineligible_sample: List[NSQFRecommendationItem] = Field(
        default_factory=list,
        description="Sample of ineligible courses with deterministic unmet criteria for transparency"
    )
    message: str = Field(..., description="Summary explanation of the recommendation run")
