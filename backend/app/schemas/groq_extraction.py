"""
Utthan Backend - Groq Conversational Understanding & Structured Extraction Schemas.
Phase 3C: Strict Structured Output Schemas for Profile Extraction and Clarification.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.adaptive_interview import AdaptiveInterviewState
from app.schemas.beneficiary import LanguageCode


class ExtractedProfileFields(BaseModel):
    """Structured fields extracted by Groq from natural-language dialogue."""
    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = Field(None, description="Citizen name if mentioned")
    education: Optional[str] = Field(None, description="Extracted schooling/education level")
    vocational_training_has: Optional[bool] = Field(None, description="True if citizen has vocational/ITI training")
    vocational_training_type: Optional[str] = Field(None, description="Type: iti, cts_ntc, cits, ats, nac, dst, etc.")
    experience_years: Optional[float] = Field(None, description="Experience in years (e.g. 0.5, 2.0, 5.0)")
    experience_domain: Optional[str] = Field(None, description="Domain or trade of practical experience")
    interested_sector_slug: Optional[str] = Field(None, description="Sector slug from authoritative 44 sectors")
    skills: List[str] = Field(default_factory=list, description="Specific skills mentioned by citizen")
    tools_familiarity: List[str] = Field(default_factory=list, description="Tools/machinery handled by citizen")
    notional_hours_range: Optional[str] = Field(None, description="Preferred duration bucket: 1–200, 201–400, etc.")
    pwd_status: Optional[bool] = Field(None, description="True if citizen explicitly identifies as PwD")
    pwd_categories: List[str] = Field(default_factory=list, description="Categories: VI, SHI, LD, ID")
    mobility_preference: Optional[str] = Field(None, description="Mobility: village_block, within_15km, etc.")
    primary_goal: Optional[str] = Field(None, description="Goal: training_stipend, job_placement, micro_business")


class ContradictionItem(BaseModel):
    """Details of a contradiction between previous profile facts and new citizen statement."""
    model_config = ConfigDict(extra="ignore")

    field: str = Field(..., description="Profile field with conflicting information")
    previous_value: Any = Field(..., description="Value recorded in prior answers")
    new_value: Any = Field(..., description="Value stated in current transcript")
    explanation: str = Field(..., description="Brief factual explanation of the contradiction")


class InterpretationResult(BaseModel):
    """
    Complete structured output from Groq LLM interpretation of beneficiary dialogue.
    Enforces strict typing and zero hallucinated reasoning.
    """
    model_config = ConfigDict(extra="ignore")

    extracted_fields: ExtractedProfileFields = Field(default_factory=ExtractedProfileFields)
    confidence: Dict[str, float] = Field(default_factory=dict, description="Field-level confidence scores 0.0 to 1.0")
    unresolved_fields: List[str] = Field(default_factory=list, description="Fields asked in stage that could not be determined")
    contradictions: List[ContradictionItem] = Field(default_factory=list, description="Contradictions with prior profile")
    needs_clarification: bool = Field(default=False, description="True if response is ambiguous, contradictory, or incomplete")
    clarification_question: Optional[str] = Field(None, description="Short, friendly clarification in citizen's active language")
    reasoning_summary: Optional[str] = Field(None, description="Brief factual reason for extraction or clarification")


class InterpretTranscriptRequest(BaseModel):
    """Request payload for interpreting a voice transcript or conversational text."""
    model_config = ConfigDict(extra="ignore")

    transcript: str = Field(..., min_length=1, max_length=2000, description="Raw transcript from Sarvam STT or citizen text")
    language: LanguageCode = Field(default="hi", description="Active interview language")
    question_id: Optional[str] = Field(None, description="Current question ID being answered")
    apply_to_profile: bool = Field(default=True, description="Automatically update session if interpretation is valid")


class InterpretTranscriptResponse(BaseModel):
    """Response returned to frontend after Groq interpretation and deterministic validation."""
    model_config = ConfigDict(extra="ignore")

    interview_id: UUID
    beneficiary_id: UUID
    interpretation: InterpretationResult
    updated_state: Optional[AdaptiveInterviewState] = None
    clarification_needed: bool = False
    clarification_question: Optional[str] = None


class ExplainRecommendationsRequest(BaseModel):
    """Payload to request natural language explanation of deterministic NSQF recommendations."""
    interview_id: Optional[UUID] = None
    language: LanguageCode = Field(default="hi", description="Language for conversational explanation")
    top_n: int = Field(default=3, ge=1, le=5, description="Number of top ranked recommendations to explain")


class RecommendationExplanationItem(BaseModel):
    """Conversational summary of why an authoritative course matched the citizen."""
    q_code: str
    title: str
    sector_name: str
    nsqf_level: float
    rank: int
    spoken_summary: str = Field(..., description="Factual conversational explanation in citizen's language")
    key_match_reasons: List[str] = Field(default_factory=list)


class ExplainRecommendationsResponse(BaseModel):
    """Natural conversational explanation grounded strictly in deterministic match reasons."""
    beneficiary_id: UUID
    interview_id: Optional[UUID] = None
    language: LanguageCode
    overall_explanation: str = Field(..., description="Holistic spoken summary of all recommendations")
    items: List[RecommendationExplanationItem] = Field(default_factory=list)

