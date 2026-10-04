"""
Utthan Backend - Pydantic Schemas for Authoritative NSQF / NQR Course Catalog.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NSQFSectorBase(BaseModel):
    id: str = Field(..., description="Unique slugified identifier for the sector")
    name: str = Field(..., description="Official sector name")
    course_count: int = Field(default=0, description="Total active courses in this sector")
    is_excluded: bool = Field(default=False, description="Whether this sector is excluded from recommendations")


class NSQFSectorOut(NSQFSectorBase):
    pass


class NSQFQualificationSummary(BaseModel):
    id: str = Field(..., description="UUID or unique ID of the qualification")
    q_code: str = Field(..., description="Official NQR qualification code")
    title: str = Field(..., description="Official qualification title")
    sector_id: str = Field(..., description="Sector slug")
    sector_name: str = Field(..., description="Sector display name")
    nsqf_level: float = Field(..., description="NSQF level (e.g. 1.0, 2.5, 4.0, 5.5, 7.0)")
    notional_hours_range: Optional[str] = Field(None, description="Notional training hours category")
    min_notional_hours: Optional[int] = Field(None, description="Minimum training hours")
    max_notional_hours: Optional[int] = Field(None, description="Maximum training hours")
    is_pwd: bool = Field(default=False, description="True if designed for Persons with Disability")
    pwd_categories: List[str] = Field(default_factory=list, description="Target disability categories (LD, SHI, VI, ID)")
    awarding_body: Optional[str] = Field(None, description="Awarding Body / SSC")


class NSQFQualificationDetail(NSQFQualificationSummary):
    description: Optional[str] = Field(None, description="Comprehensive role overview and description")
    version: Optional[str] = Field(None, description="Qualification pack version")
    originally_approved: Optional[str] = Field(None, description="Date of original NCVET/NSQC approval")
    valid_till: Optional[str] = Field(None, description="Validity end date")
    certifying_bodies: Optional[str] = Field(None, description="Recognized certifying bodies")
    proposed_occupation: Optional[str] = Field(None, description="National Classification of Occupations job role")
    progression_pathway: Optional[str] = Field(None, description="Career and educational progression pathway")
    qualification_type: Optional[str] = Field(None, description="Qualification category")
    adopted_qualification: Optional[str] = Field(None, description="Reference to parent adopted qualification")
    training_delivery_hours: Optional[str] = Field(None, description="Breakdown of delivery hours")
    source_file: Optional[str] = Field(None, description="Originating dataset workbook filename")
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw source metadata preserved for auditability")


class NSQFCatalogResponse(BaseModel):
    items: List[NSQFQualificationSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class NSQFCatalogStats(BaseModel):
    total_courses: int
    total_sectors: int
    excluded_sectors_count: int
    pwd_courses_count: int
    levels_distribution: Dict[str, int]
    hours_distribution: Dict[str, int]
    top_sectors: List[Dict[str, Any]]
