"""
Utthan Backend - Pydantic Schemas for Adaptive Beneficiary Interview & Structured Profile.
Phase 3B: Adaptive Interview Engine + Structured Beneficiary Profile.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.beneficiary import LanguageCode


class InterviewStage(str, Enum):
    LOCATION = "location"
    BASIC_PROFILE = "basic_profile"
    EDUCATION = "education"
    VOCATIONAL_TRAINING = "vocational_training"
    EXPERIENCE = "experience"
    SECTOR = "sector"
    CATALOG_CONTEXT = "catalog_context"
    COMPETENCY_EVIDENCE = "competency_evidence"
    CAPACITY_HOURS = "capacity_hours"
    PWD = "pwd"
    WORK_PREFERENCES = "work_preferences"
    REVIEW = "review"
    COMPLETED = "completed"


class QuestionInputType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    TEXT = "text"
    NUMBER = "number"
    YES_NO = "yes_no"
    VOICE_TEXT = "voice_text"
    LOCATION_SELECT = "location_select"


class InputMethod(str, Enum):
    VOICE = "voice"
    OPTION = "option"
    MANUAL = "manual"


class QuestionOption(BaseModel):
    value: str = Field(..., description="Canonical value for backend persistence")
    label: str = Field(..., description="Localized display label")
    icon: Optional[str] = Field(None, description="Optional emoji or icon representation")
    description: Optional[str] = Field(None, description="Secondary helper text")


class AdaptiveQuestion(BaseModel):
    question_id: str = Field(..., description="Unique question identifier")
    stage: InterviewStage = Field(..., description="Current interview stage")
    title: str = Field(..., description="Short stage or category header")
    question_text: str = Field(..., description="Full spoken/displayed question in beneficiary language")
    input_type: QuestionInputType = Field(default=QuestionInputType.SINGLE_CHOICE)
    options: List[QuestionOption] = Field(default_factory=list)
    required: bool = Field(default=True)
    field_target: str = Field(..., description="Target profile field (e.g., 'education', 'interested_sector')")
    catalog_context: Optional[Dict[str, Any]] = Field(None, description="Authoritative NQR course context if grounded in catalog")
    reason: Optional[str] = Field(None, description="Why this adaptive question is being asked")
    help_text: Optional[str] = Field(None, description="Contextual guidance for citizen or field worker")
    is_clarification: bool = Field(default=False, description="True if asked because prior answer was incomplete/ambiguous")


class AdaptiveAnswerSubmit(BaseModel):
    model_config = ConfigDict(extra="ignore")

    question_id: str = Field(..., description="ID of question being answered")
    raw_answer: str = Field(..., description="Raw text, transcription, or selected option")
    normalized_answer: Any = Field(..., description="Canonical value (e.g. '10th_pass', 'agriculture', 2.0, True)")
    input_method: InputMethod = Field(default=InputMethod.OPTION)
    language: LanguageCode = Field(default="hi")


class NSQFCompetencyEvidence(BaseModel):
    """Evidence mapped to the five official NSQF descriptor dimensions."""
    professional_knowledge: List[str] = Field(default_factory=list, description="Knowledge of facts, principles, processes")
    technical_skills: List[str] = Field(default_factory=list, description="Practical skills, tool/equipment handling")
    core_skills: List[str] = Field(default_factory=list, description="Communication, basic numeracy, digital literacy")
    process_capability: List[str] = Field(default_factory=list, description="Routine, non-routine, or specialized work capability")
    responsibility_level: Optional[str] = Field(None, description="No responsibility/supervised, some autonomy, or independent/supervisory")


class StructuredBeneficiaryProfile(BaseModel):
    """
    Comprehensive structured citizen profile produced by the adaptive interview.
    Consumed by the downstream deterministic recommendation engine.
    """
    beneficiary_id: UUID
    interview_id: UUID
    preferred_language: LanguageCode = "hi"
    name: Optional[str] = None
    state_id: Optional[str] = None
    state_name: Optional[str] = None
    district_id: Optional[str] = None
    district_name: Optional[str] = None

    # Education & Training
    education: Optional[str] = Field(None, description="Canonical education level (e.g. 'no_formal', '8th_pass', '10th_pass', '12th_pass', 'diploma', 'iti_vocational', 'graduate')")
    education_label: Optional[str] = None
    previous_nsqf_qualification: Optional[str] = None
    vocational_training: bool = Field(default=False)
    vocational_training_type: Optional[str] = None  # None, ITI, CTS, CITS, ATS, etc.

    # Experience
    work_experience_years: float = Field(default=0.0, description="Total experience in years (e.g. 0.0, 0.5, 2.0, 5.0)")
    work_experience_label: Optional[str] = None
    current_occupation: Optional[str] = None

    # Sector & Course Preferences
    interested_sector_id: Optional[str] = Field(None, description="Sector slug from authoritative nsqf_sectors")
    interested_sector_name: Optional[str] = None
    target_qualifications: List[str] = Field(default_factory=list, description="List of q_codes identified during adaptive interview")
    notional_hours_range: Optional[str] = Field(None, description="Preferred course duration bucket (e.g. '401–600')")

    # Inclusion & Accessibility
    pwd_status: bool = Field(default=False)
    pwd_categories: List[str] = Field(default_factory=list, description="Categories (VI, SHI, LD, ID, etc.)")
    pwd_checked: bool = Field(default=False, description="True once PwD status question has been answered")

    # Practical Competencies & Evidence
    skills: List[str] = Field(default_factory=list)
    competencies: List[str] = Field(default_factory=list)
    tools_familiarity: List[str] = Field(default_factory=list)
    competency_evidence: NSQFCompetencyEvidence = Field(default_factory=NSQFCompetencyEvidence)

    # Work & Life Preferences
    mobility_preference: Optional[str] = Field("within_15km", description="'village_block', 'within_15km', 'district_wide', 'relocate_hostel'")
    primary_goal: Optional[str] = Field("training_stipend", description="'training_stipend', 'job_placement', 'micro_business'")

    # Metadata
    completeness_percentage: int = Field(default=0, ge=0, le=100)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AdaptiveInterviewState(BaseModel):
    """
    Active state returned to frontend to render current question, progress, and history.
    """
    interview_id: UUID
    beneficiary_id: UUID
    language: LanguageCode = "hi"
    current_stage: InterviewStage
    stage_index: int = Field(..., description="0-indexed current stage position")
    total_stages: int = Field(default=12)
    current_question: Optional[AdaptiveQuestion] = None
    answered_questions_count: int = 0
    completeness_percentage: int = 0
    can_go_back: bool = False
    is_completed: bool = False
    profile_summary: Optional[StructuredBeneficiaryProfile] = None


class ProfileFieldCorrectionRequest(BaseModel):
    field_name: str = Field(..., description="Field in StructuredBeneficiaryProfile to update")
    value: Any = Field(..., description="New value")
