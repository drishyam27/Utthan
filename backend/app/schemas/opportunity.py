"""
Opportunities and Skills Schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SkillBrief(BaseModel):
    id: str = Field(..., examples=["skill-solar-inst"])
    name: str = Field(..., examples=["Solar PV Rooftop Installation"])
    sector: Optional[str] = Field(None, examples=["Green Jobs & Renewable Energy"])
    nsqf_level: Optional[int] = Field(None, examples=[4])
    qp_code: Optional[str] = Field(None, examples=["SGJ/Q0101"])
    is_primary: Optional[bool] = Field(True, examples=[True])


class OpportunityBrief(BaseModel):
    id: str = Field(..., examples=["opp-pm-vishwakarma-solar"])
    title: str = Field(..., examples=["PM Vishwakarma - Solar PV Installation"])
    category: str = Field(..., examples=["Green Energy & Technology"])
    provider: str = Field(..., examples=["Ministry of Micro, Small & Medium Enterprises"])
    source: str = Field(..., examples=["PM Vishwakarma Official Portal"])
    source_url: Optional[str] = Field(None, examples=["https://pmvishwakarma.gov.in"])
    state_id: Optional[str] = Field(None, examples=[None])
    district_id: Optional[str] = Field(None, examples=[None])
    education_min: str = Field(..., examples=["no_formal"])
    age_min: Optional[int] = Field(18, examples=[18])
    age_max: Optional[int] = Field(None, examples=[None])
    mobility_requirement: Optional[str] = Field("within_15km", examples=["within_15km"])
    stipend: Optional[str] = Field(None, examples=["Rs 500/day during 5-day basic training"])
    duration: Optional[str] = Field(None, examples=["5 days basic + 15 days advanced"])


class OpportunityDetail(OpportunityBrief):
    expected_earnings: Optional[str] = Field(None, examples=["Rs 15,000 - 25,000/month after certification"])
    skills: List[SkillBrief] = Field(default_factory=list)


class OpportunityListResponse(BaseModel):
    total: int = Field(..., examples=[7])
    opportunities: List[OpportunityBrief]
