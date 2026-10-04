"""
Utthan Backend - NSQF / NQR Course Catalog Routes.
Provides public catalog discovery endpoints for authoritative NSQF qualifications.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.db.supabase import get_supabase_client
from app.schemas.nsqf import (
    NSQFCatalogResponse,
    NSQFCatalogStats,
    NSQFQualificationDetail,
    NSQFSectorOut,
)
from app.services.nsqf_service import (
    get_catalog_stats,
    get_course_detail,
    list_sectors,
    query_courses,
)

router = APIRouter(prefix="/nsqf", tags=["NSQF Catalog"])


@router.get(
    "/sectors",
    response_model=List[NSQFSectorOut],
    summary="List NSQF Industry Sectors",
    description="Returns all active industry sectors in the authoritative NQR catalog with qualification counts.",
)
def get_nsqf_sectors(
    client: Optional[Client] = Depends(get_supabase_client),
    include_excluded: bool = Query(False, description="Whether to include excluded sectors"),
) -> List[NSQFSectorOut]:
    return list_sectors(client=client, include_excluded=include_excluded)


@router.get(
    "/courses",
    response_model=NSQFCatalogResponse,
    summary="Search & Filter NSQF Qualifications",
    description=(
        "Query official qualifications by sector, NSQF level, notional hours, "
        "PwD applicability, and free-text search."
    ),
)
def search_nsqf_courses(
    client: Optional[Client] = Depends(get_supabase_client),
    sector_id: Optional[str] = Query(None, description="Sector slug or name filter"),
    nsqf_level: Optional[float] = Query(None, description="Exact NSQF level (e.g. 4.0, 2.5)"),
    min_level: Optional[float] = Query(None, description="Minimum NSQF level"),
    max_level: Optional[float] = Query(None, description="Maximum NSQF level"),
    notional_hours_range: Optional[str] = Query(None, description="Hours bucket (e.g. '401–600')"),
    is_pwd: Optional[bool] = Query(None, description="Filter for Persons with Disability courses"),
    pwd_category: Optional[str] = Query(None, description="Target disability category (LD, SHI, VI, ID)"),
    search: Optional[str] = Query(None, description="Search term in title, description, or occupation"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> NSQFCatalogResponse:
    return query_courses(
        client=client,
        sector_id=sector_id,
        nsqf_level=nsqf_level,
        min_level=min_level,
        max_level=max_level,
        notional_hours_range=notional_hours_range,
        is_pwd=is_pwd,
        pwd_category=pwd_category,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/courses/{course_id:path}",
    response_model=NSQFQualificationDetail,
    summary="Get NSQF Qualification Details",
    description="Retrieve full syllabus, progression, and metadata for a specific qualification by ID or q_code.",
)
def get_nsqf_course_by_id(
    course_id: str,
    client: Optional[Client] = Depends(get_supabase_client),
) -> NSQFQualificationDetail:
    course = get_course_detail(course_id=course_id, client=client)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Qualification with ID or code '{course_id}' was not found in catalog.",
        )
    return course


@router.get(
    "/stats",
    response_model=NSQFCatalogStats,
    summary="Get NSQF Catalog Statistics",
    description="Aggregate metrics across levels, hours, sectors, and PwD applicability.",
)
def get_nsqf_catalog_statistics(
    client: Optional[Client] = Depends(get_supabase_client),
) -> NSQFCatalogStats:
    return get_catalog_stats(client=client)
