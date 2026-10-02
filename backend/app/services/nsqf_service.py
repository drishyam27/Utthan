"""
Utthan Backend - Authoritative NSQF / NQR Catalog Service Layer.
Provides high-performance querying and filtering over authoritative NSQF qualifications.
Supports both Supabase PostgreSQL queries and high-performance in-memory cached fallback.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from supabase import Client

from app.schemas.nsqf import (
    NSQFSectorOut,
    NSQFQualificationSummary,
    NSQFQualificationDetail,
    NSQFCatalogResponse,
    NSQFCatalogStats,
)
from app.services.nsqf_ingestion import parse_all_courses

logger = logging.getLogger("utthan.nsqf_service")

# In-memory singleton cache for instant lookups & offline resilience
_CACHED_SECTORS: Optional[List[Dict[str, Any]]] = None
_CACHED_COURSES: Optional[List[Dict[str, Any]]] = None
_CACHED_STATS: Optional[Dict[str, Any]] = None


def _get_in_memory_catalog() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """Loads and caches the parsed course catalog in memory."""
    global _CACHED_SECTORS, _CACHED_COURSES, _CACHED_STATS
    if _CACHED_COURSES is None or _CACHED_SECTORS is None:
        sectors, courses, metrics = parse_all_courses()
        # assign deterministic in-memory IDs if needed
        for idx, c in enumerate(courses):
            if "id" not in c:
                c["id"] = f"nsqf-{c['sector_id']}-{idx+1}"
        _CACHED_SECTORS = sectors
        _CACHED_COURSES = courses
        _CACHED_STATS = metrics
    return _CACHED_SECTORS, _CACHED_COURSES, _CACHED_STATS


def list_sectors(
    client: Optional[Client] = None,
    include_excluded: bool = False,
) -> List[NSQFSectorOut]:
    """
    Returns list of all active NSQF industry sectors with course counts.
    """
    if client is not None:
        try:
            query = client.table("nsqf_sectors").select("*").order("name")
            if not include_excluded:
                query = query.eq("is_excluded", False)
            res = query.execute()
            if res.data:
                return [NSQFSectorOut(**row) for row in res.data]
        except Exception as exc:
            logger.warning(f"Failed to query nsqf_sectors from Supabase: {exc}; using local catalog fallback.")

    sectors, _, _ = _get_in_memory_catalog()
    filtered = [s for s in sectors if include_excluded or not s.get("is_excluded", False)]
    filtered.sort(key=lambda x: x["name"])
    return [NSQFSectorOut(**s) for s in filtered]


def query_courses(
    client: Optional[Client] = None,
    sector_id: Optional[str] = None,
    nsqf_level: Optional[float] = None,
    min_level: Optional[float] = None,
    max_level: Optional[float] = None,
    notional_hours_range: Optional[str] = None,
    is_pwd: Optional[bool] = None,
    pwd_category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> NSQFCatalogResponse:
    """
    Multi-criteria filter and search over authoritative NSQF qualifications.
    """
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    offset = (page - 1) * page_size

    # Try Supabase if available
    if client is not None:
        try:
            query = client.table("nsqf_qualifications").select(
                "id, q_code, title, sector_id, sector_name, nsqf_level, notional_hours_range, min_notional_hours, max_notional_hours, is_pwd, pwd_categories, awarding_body",
                count="exact"
            ).eq("is_active", True)

            if sector_id:
                query = query.eq("sector_id", sector_id.lower().strip())
            if nsqf_level is not None:
                query = query.eq("nsqf_level", nsqf_level)
            if min_level is not None:
                query = query.gte("nsqf_level", min_level)
            if max_level is not None:
                query = query.lte("nsqf_level", max_level)
            if notional_hours_range:
                query = query.eq("notional_hours_range", notional_hours_range)
            if is_pwd is not None:
                query = query.eq("is_pwd", is_pwd)
            if pwd_category:
                query = query.contains("pwd_categories", [pwd_category.upper()])
            if search:
                pattern = f"%{search.strip()}%"
                query = query.ilike("title", pattern)

            query = query.order("title").range(offset, offset + page_size - 1)
            res = query.execute()
            if res.data is not None:
                items = [NSQFQualificationSummary(**row) for row in res.data]
                total = res.count if res.count is not None else len(items)
                total_pages = (total + page_size - 1) // page_size if total > 0 else 1
                return NSQFCatalogResponse(
                    items=items,
                    total=total,
                    page=page,
                    page_size=page_size,
                    total_pages=total_pages
                )
        except Exception as exc:
            logger.warning(f"Failed to query nsqf_qualifications from Supabase: {exc}; using local catalog fallback.")

    # Local fallback query
    _, courses, _ = _get_in_memory_catalog()
    results = courses

    if sector_id:
        target_sector = sector_id.lower().strip()
        results = [c for c in results if c["sector_id"] == target_sector or c["sector_name"].lower() == target_sector]

    if nsqf_level is not None:
        results = [c for c in results if c["nsqf_level"] == nsqf_level]

    if min_level is not None:
        results = [c for c in results if c["nsqf_level"] >= min_level]

    if max_level is not None:
        results = [c for c in results if c["nsqf_level"] <= max_level]

    if notional_hours_range:
        results = [c for c in results if c.get("notional_hours_range") == notional_hours_range]

    if is_pwd is not None:
        results = [c for c in results if c.get("is_pwd") == is_pwd]

    if pwd_category:
        cat_upper = pwd_category.upper().strip()
        results = [c for c in results if cat_upper in c.get("pwd_categories", [])]

    if search:
        s_lower = search.lower().strip()
        results = [
            c for c in results
            if s_lower in c["title"].lower()
            or s_lower in c.get("description", "").lower()
            or s_lower in c.get("proposed_occupation", "").lower()
            or s_lower in c["q_code"].lower()
        ]

    total = len(results)
    paged = results[offset:offset + page_size]
    items = [NSQFQualificationSummary(**c) for c in paged]
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return NSQFCatalogResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


def get_course_detail(
    course_id: str,
    client: Optional[Client] = None,
) -> Optional[NSQFQualificationDetail]:
    """
    Retrieves full details of a qualification by ID or q_code.
    """
    if client is not None:
        try:
            res = client.table("nsqf_qualifications").select("*").or_(
                f"id.eq.{course_id},q_code.eq.{course_id}"
            ).limit(1).execute()
            if res.data and len(res.data) > 0:
                return NSQFQualificationDetail(**res.data[0])
        except Exception as exc:
            logger.warning(f"Failed to get course detail from Supabase: {exc}; using local catalog fallback.")

    _, courses, _ = _get_in_memory_catalog()
    for c in courses:
        if c.get("id") == course_id or c.get("q_code") == course_id:
            return NSQFQualificationDetail(**c)
    return None


def get_catalog_stats(client: Optional[Client] = None) -> NSQFCatalogStats:
    """
    Calculates statistical aggregates across the catalog.
    """
    sectors, courses, metrics = _get_in_memory_catalog()
    
    top_sectors = [
        {"id": s["id"], "name": s["name"], "count": s["course_count"]}
        for s in sorted(sectors, key=lambda x: -x["course_count"])[:10]
    ]

    return NSQFCatalogStats(
        total_courses=len(courses),
        total_sectors=len(sectors),
        excluded_sectors_count=len(metrics.get("excluded_sectors_found", [])),
        pwd_courses_count=metrics.get("pwd_count", 0),
        levels_distribution=dict(sorted(metrics.get("levels", {}).items(), key=lambda x: float(x[0]))),
        hours_distribution=dict(metrics.get("hour_ranges", {})),
        top_sectors=top_sectors,
    )
