"""
Opportunities Catalog API Routes.
Queries verified government schemes, subsidized skilling courses, and grants from Supabase.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from supabase import Client
from app.db.supabase import get_supabase_client
from app.schemas.opportunity import (
    OpportunityBrief,
    OpportunityDetail,
    OpportunityListResponse,
    SkillBrief
)
from app.schemas.common import ErrorResponse

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get(
    "",
    response_model=OpportunityListResponse,
    summary="List Opportunities Catalog",
    description="Returns verified government opportunities with optional filters for location, education, and mobility."
)
def list_opportunities(
    state_id: Optional[str] = Query(None, description="Filter by State ID (or Pan-India opportunities)"),
    category: Optional[str] = Query(None, description="Filter by opportunity category / sector"),
    education: Optional[str] = Query(None, description="Filter by minimum education level"),
    mobility: Optional[str] = Query(None, description="Filter by mobility requirement"),
    client: Client = Depends(get_supabase_client)
):
    try:
        query = client.table("opportunities").select(
            "id, title, category, provider, source, source_url, "
            "state_id, district_id, education_min, age_min, age_max, "
            "mobility_requirement, stipend, duration"
        )

        if category:
            query = query.ilike("category", f"%{category}%")
        if education:
            query = query.eq("education_min", education)
        if mobility:
            query = query.eq("mobility_requirement", mobility)

        response = query.order("title").execute()
        rows = response.data or []

        # If state_id is provided, include schemes matching state_id PLUS Pan-India schemes (where state_id is null)
        if state_id:
            rows = [r for r in rows if r.get("state_id") is None or r.get("state_id") == state_id]

        opportunities = [OpportunityBrief(**r) for r in rows]
        return OpportunityListResponse(
            total=len(opportunities),
            opportunities=opportunities
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(exc)}"
        )


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityDetail,
    responses={404: {"model": ErrorResponse, "description": "Opportunity not found"}},
    summary="Get Opportunity Details with Mapped Skills",
    description="Returns comprehensive details for a specific opportunity, including associated NSQF standardized skills."
)
def get_opportunity(opportunity_id: str, client: Client = Depends(get_supabase_client)):
    try:
        opp_res = client.table("opportunities").select("*").eq("id", opportunity_id).execute()
        if not opp_res.data or len(opp_res.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity with ID '{opportunity_id}' not found in catalog."
            )

        opp_data = opp_res.data[0]

        # Fetch mapped skills
        skills: list[SkillBrief] = []
        try:
            mapping_res = client.table("opportunity_skills").select(
                "skill_id, is_primary, skills(id, name, sector, nsqf_level, qp_code)"
            ).eq("opportunity_id", opportunity_id).execute()

            for item in (mapping_res.data or []):
                skill_obj = item.get("skills")
                if skill_obj and isinstance(skill_obj, dict):
                    skills.append(SkillBrief(
                        id=skill_obj["id"],
                        name=skill_obj["name"],
                        sector=skill_obj.get("sector"),
                        nsqf_level=skill_obj.get("nsqf_level"),
                        qp_code=skill_obj.get("qp_code"),
                        is_primary=item.get("is_primary", True)
                    ))
                elif item.get("skill_id"):
                    # Direct lookup if relation not embedded
                    s_id = item["skill_id"]
                    s_res = client.table("skills").select("id, name, sector, nsqf_level, qp_code").eq("id", s_id).execute()
                    if s_res.data and len(s_res.data) > 0:
                        s = s_res.data[0]
                        skills.append(SkillBrief(
                            id=s["id"],
                            name=s["name"],
                            sector=s.get("sector"),
                            nsqf_level=s.get("nsqf_level"),
                            qp_code=s.get("qp_code"),
                            is_primary=item.get("is_primary", True)
                        ))
        except Exception:
            skills = []

        return OpportunityDetail(
            id=opp_data["id"],
            title=opp_data["title"],
            category=opp_data["category"],
            provider=opp_data["provider"],
            source=opp_data["source"],
            source_url=opp_data.get("source_url"),
            state_id=opp_data.get("state_id"),
            district_id=opp_data.get("district_id"),
            education_min=opp_data.get("education_min", "no_formal"),
            age_min=opp_data.get("age_min", 18),
            age_max=opp_data.get("age_max"),
            mobility_requirement=opp_data.get("mobility_requirement", "within_15km"),
            stipend=opp_data.get("stipend"),
            expected_earnings=opp_data.get("expected_earnings"),
            duration=opp_data.get("duration"),
            skills=skills
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch opportunity '{opportunity_id}': {str(exc)}"
        )
