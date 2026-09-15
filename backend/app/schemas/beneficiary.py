"""Typed beneficiary profile contracts for the Phase 2C persistence boundary."""

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


LanguageCode = Literal[
    "en", "hi", "bn", "te", "mr", "ta", "ur", "gu", "kn", "ml", "or",
    "pa", "as", "mai", "sa", "ne", "kok", "sd", "ks", "dgo", "mni", "brx", "sat",
]
EducationLevel = Literal[
    "no_formal", "8th_pass", "10th_pass", "12th_pass", "iti_vocational", "graduate",
]
MobilityPreference = Literal[
    "village_block", "within_15km", "district_wide", "relocate_hostel",
]
PrimaryGoal = Literal["training_stipend", "job_placement", "micro_business"]


class BeneficiaryProfileContract(BaseModel):
    """Stable beneficiary fields shared by later persistence and recommendation APIs."""

    id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    preferred_language: LanguageCode = "hi"
    state_id: Optional[str] = Field(None, min_length=1, max_length=32)
    district_id: Optional[str] = Field(None, min_length=1, max_length=64)
    education_level: Optional[EducationLevel] = "no_formal"
    current_occupation: Optional[str] = Field(None, max_length=150)
    mobility_preference: Optional[MobilityPreference] = "within_15km"
    primary_goal: Optional[PrimaryGoal] = "training_stipend"


class BeneficiarySessionProfile(BaseModel):
    """Profile values permitted in a later anonymous session-bound workflow."""

    preferred_language: LanguageCode = "hi"
    state_id: Optional[str] = Field(None, min_length=1, max_length=32)
    district_id: Optional[str] = Field(None, min_length=1, max_length=64)
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    education_level: Optional[EducationLevel] = "no_formal"
    current_occupation: Optional[str] = Field(None, max_length=150)
    mobility_preference: Optional[MobilityPreference] = "within_15km"
    primary_goal: Optional[PrimaryGoal] = "training_stipend"
