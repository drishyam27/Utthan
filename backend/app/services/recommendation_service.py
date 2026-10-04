"""Deterministic Recommendation Service for Utthan.

Provides server-side, explainable, rule-based matching between
beneficiary candidate profiles (from completed interviews) and verified
government livelihood schemes. Zero LLM hallucination in eligibility decisions.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Optional
from uuid import UUID

from supabase import Client

from app.schemas.recommendation import (
    RecommendationResponseContract,
    RecommendationResultContract,
    RecommendationSkillMetadata,
)
from app.services.beneficiary_service import BeneficiaryNotFoundError

logger = logging.getLogger(__name__)

EDUCATION_LEVEL_RANKS: dict[str, int] = {
    "no_formal": 1,
    "8th_pass": 2,
    "10th_pass": 3,
    "12th_pass": 4,
    "iti_vocational": 5,
    "graduate": 6,
}

MOBILITY_LEVEL_RANKS: dict[str, int] = {
    "village_block": 1,
    "within_15km": 2,
    "district_wide": 3,
    "relocate_hostel": 4,
}


def _rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    return data if isinstance(data, list) else []


def _first(response: Any) -> Optional[dict[str, Any]]:
    rows = _rows(response)
    return rows[0] if rows else None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_education(input_val: Any = "") -> str:
    """Normalize human survey or interview answers to canonical education keys."""
    text = str(input_val or "").strip().lower()
    if "graduat" in text or "degree" in text or "স্নাতক" in text:
        return "graduate"
    if "iti" in text or "diploma" in text or "vocational" in text or "আইটিআই" in text:
        return "iti_vocational"
    if "12" in text or "higher" in text or "উচ্চমাধ্যমিক" in text or "12वीं" in text:
        return "12th_pass"
    if "10" in text or "matric" in text or "secondary" in text or "মাধ্যমিক" in text or "10वीं" in text:
        return "10th_pass"
    if "8" in text or "middle" in text or "৮ম" in text or "8वीं" in text:
        return "8th_pass"
    return "no_formal"


def normalize_mobility(input_val: Any = "") -> str:
    """Normalize travel preference answers to canonical mobility keys."""
    text = str(input_val or "").strip().lower()
    if "relocate" in text or "hostel" in text or "হোস্টেল" in text or "बाहर" in text:
        return "relocate_hostel"
    if "district" in text or "জেলা" in text or "जिले" in text:
        return "district_wide"
    if "15" in text or "km" in text or "town" in text or "কসবা" in text or "शहर" in text:
        return "within_15km"
    return "village_block"


def normalize_goal(input_val: Any = "") -> str:
    """Normalize milestone aspiration answers to canonical goal keys."""
    text = str(input_val or "").strip().lower()
    if (
        "shop" in text
        or "business" in text
        or "দোকান" in text
        or "व्यवसाय" in text
        or "স্বনির্ভর" in text
        or "दुकान" in text
    ):
        return "micro_business"
    if (
        "job" in text
        or "placement" in text
        or "পাক্কা চাকরি" in text
        or "पक्की नौकरी" in text
        or "কর্মসংস্থান" in text
        or "रोजगार" in text
    ):
        return "job_placement"
    return "training_stipend"


def check_hard_eligibility(
    candidate: dict[str, Any],
    opportunity: dict[str, Any],
) -> tuple[bool, list[str], list[str]]:
    """Determine hard deterministic eligibility against legal & program gates.

    Returns: (eligible: bool, matched_criteria: list[str], unmet_criteria: list[str])
    """
    rules = opportunity.get("eligibility_rules") or opportunity.get("eligibilityRules") or {}
    matched_criteria: list[str] = []
    unmet_criteria: list[str] = []

    # 1. Geographic Gate (State & District)
    is_pan_india = rules.get("panIndia") is not False and not opportunity.get("state_id") and not opportunity.get("stateId")
    if not is_pan_india:
        target_state_id = opportunity.get("state_id") or opportunity.get("stateId")
        target_district_id = opportunity.get("district_id") or opportunity.get("districtId")
        cand_state_id = candidate.get("state_id") or candidate.get("stateId")
        cand_district_id = candidate.get("district_id") or candidate.get("districtId")

        missing_canonical_location = (not cand_state_id) or (bool(target_district_id) and not cand_district_id)
        if missing_canonical_location:
            unmet_criteria.append("Canonical State and District location is required for this restricted opportunity")
        elif target_state_id and cand_state_id != target_state_id:
            unmet_criteria.append(f"Location restricted to state: {target_state_id}")
        elif target_district_id and cand_district_id != target_district_id:
            unmet_criteria.append(f"Location restricted to district: {target_district_id}")
        else:
            matched_criteria.append("Geographic location matches program jurisdiction")
    else:
        matched_criteria.append("Pan-India eligibility applies across all States and Districts")

    # 2. Minimum Education Gate
    min_edu = (
        opportunity.get("education_min")
        or opportunity.get("educationMin")
        or rules.get("minEducation")
        or "no_formal"
    )
    min_edu_rank = EDUCATION_LEVEL_RANKS.get(min_edu, 1)
    user_edu_key = normalize_education(candidate.get("education"))
    user_edu_rank = EDUCATION_LEVEL_RANKS.get(user_edu_key, 1)

    if user_edu_rank < min_edu_rank:
        unmet_criteria.append(
            f"Minimum education required is {min_edu.replace('_', ' ')} (beneficiary has {user_edu_key.replace('_', ' ')})"
        )
    else:
        matched_criteria.append(f"Meets education qualification threshold ({user_edu_key.replace('_', ' ')})")

    # 3. Age Limits Gate (if candidate age is provided and positive)
    raw_age = candidate.get("age")
    try:
        user_age = int(raw_age) if raw_age is not None else None
    except (ValueError, TypeError):
        user_age = None

    if user_age is not None and user_age > 0:
        min_age = rules.get("minAge") or opportunity.get("age_min")
        max_age = rules.get("maxAge") or opportunity.get("age_max")
        if min_age and user_age < min_age:
            unmet_criteria.append(f"Minimum age required is {min_age} (beneficiary is {user_age})")
        elif max_age and user_age > max_age:
            unmet_criteria.append(f"Maximum age allowed is {max_age} (beneficiary is {user_age})")
        else:
            matched_criteria.append(f"Age ({user_age} years) within permissible bounds")

    # 4. Mobility Requirement Gate
    req_mobility = (
        opportunity.get("mobility_requirement")
        or opportunity.get("mobilityRequirement")
        or "within_15km"
    )
    req_mobility_rank = MOBILITY_LEVEL_RANKS.get(req_mobility, 2)
    user_mobility_key = normalize_mobility(candidate.get("mobility"))
    user_mobility_rank = MOBILITY_LEVEL_RANKS.get(user_mobility_key, 1)

    accepted_mobility = rules.get("acceptedMobility") or rules.get("accepted_mobility") or []
    if user_mobility_rank < req_mobility_rank and (user_mobility_key not in accepted_mobility):
        unmet_criteria.append(
            f"Opportunity requires travel: {req_mobility.replace('_', ' ')} (beneficiary prefers: {user_mobility_key.replace('_', ' ')})"
        )
    else:
        matched_criteria.append(
            f"Mobility preference matches commute requirements ({user_mobility_key.replace('_', ' ')})"
        )

    eligible = len(unmet_criteria) == 0
    return eligible, matched_criteria, unmet_criteria


def calculate_match_score(
    candidate: dict[str, Any],
    opportunity: dict[str, Any],
) -> tuple[int, list[str]]:
    """Compute weighted deterministic match score (0-100) and explainable reasons.

    Weights:
    - Trade / Skills Alignment: 40%
    - Mobility Fit: 25%
    - Education Fit: 20%
    - Goal / Priority Fit: 15%
    """
    score = 0
    reasons: list[str] = []

    # A. Trade Alignment (40 pts max)
    target_keywords = (
        opportunity.get("target_trade_keywords")
        or opportunity.get("targetTradeKeywords")
        or []
    )
    user_trade = str(
        candidate.get("trade") or candidate.get("workInterest") or candidate.get("current_occupation") or ""
    ).strip().lower()

    keyword_match = False
    if user_trade:
        for kw in target_keywords:
            kw_clean = str(kw).strip().lower()
            if kw_clean and (kw_clean in user_trade or user_trade in kw_clean):
                keyword_match = True
                break

    if keyword_match:
        score += 40
        reasons.append(f"Direct alignment with your selected craft/trade interest ({user_trade})")
    else:
        cat = str(opportunity.get("category") or "").strip().lower()
        cat_primary = cat.split("/")[0].strip()
        if user_trade and (cat in user_trade or user_trade in cat or cat_primary in user_trade):
            score += 25
            reasons.append(f"Related to your broader industry focus ({opportunity.get('category')})")
        else:
            score += 15
            reasons.append(f"Accessible foundation track for cross-skilling into {opportunity.get('category', 'skilling')}")

    # B. Mobility Fit (25 pts max)
    user_mobility = normalize_mobility(candidate.get("mobility"))
    opp_mobility = (
        opportunity.get("mobility_requirement")
        or opportunity.get("mobilityRequirement")
        or "within_15km"
    )
    if user_mobility == opp_mobility:
        score += 25
        reasons.append(f"Convenient distance matching your exact travel preference ({user_mobility.replace('_', ' ')})")
    else:
        score += 18
        reasons.append("Commute falls within feasible regional distance")

    # C. Education Fit (20 pts max)
    user_edu = normalize_education(candidate.get("education"))
    min_edu = (
        opportunity.get("education_min")
        or opportunity.get("educationMin")
        or "no_formal"
    )
    if user_edu == min_edu:
        score += 20
        reasons.append("Optimal qualification match for curriculum pace")
    else:
        score += 17
        reasons.append("Exceeds base qualification requirement, enabling faster completion")

    # D. Goal Fit (15 pts max)
    user_goal = normalize_goal(
        candidate.get("goal") or candidate.get("preference") or candidate.get("primary_goal")
    )
    opp_goal = (
        opportunity.get("primary_goal_fit")
        or opportunity.get("primaryGoalFit")
        or "training_stipend"
    )
    if user_goal == opp_goal:
        score += 15
        reasons.append(f"Directly fulfills your milestone goal ({user_goal.replace('_', ' ')})")
    else:
        score += 10
        reasons.append("Includes complementary pathways toward your future aspirations")

    bounded_score = min(100, max(0, score))
    return bounded_score, reasons


def generate_recommendations(
    client: Client,
    beneficiary_id: UUID,
) -> RecommendationResponseContract:
    """Generate deterministic recommendations from persisted server-side data."""
    # 1. Fetch Beneficiary
    ben_res = client.table("beneficiaries").select("*").eq("id", str(beneficiary_id)).limit(1).execute()
    beneficiary = _first(ben_res)
    if not beneficiary:
        raise BeneficiaryNotFoundError(f"Beneficiary {beneficiary_id} not found.")

    state_id = beneficiary.get("state_id")
    district_id = beneficiary.get("district_id")

    # 2. Fetch Latest Completed Interview
    interview_res = (
        client.table("interview_sessions")
        .select("*")
        .eq("beneficiary_id", str(beneficiary_id))
        .eq("status", "completed")
        .order("completed_at", desc=True)
        .limit(1)
        .execute()
    )
    completed_interview = _first(interview_res)

    if not completed_interview:
        # Check if there is an in-progress draft session
        draft_res = (
            client.table("interview_sessions")
            .select("id")
            .eq("beneficiary_id", str(beneficiary_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        draft = _first(draft_res)
        draft_id = UUID(str(draft["id"])) if draft and draft.get("id") else None

        return RecommendationResponseContract(
            beneficiary_id=beneficiary_id,
            state_id=state_id,
            district_id=district_id,
            interview_id=draft_id,
            has_completed_interview=False,
            generated_at=_now(),
            message="An interview must be completed before recommendations can be generated.",
            recommendations=[],
            ineligible_opportunities=[],
        )

    interview_id = UUID(str(completed_interview["id"]))
    responses = completed_interview.get("responses") or {}

    # 3. Assemble Normalized Candidate Profile from Persisted Data
    candidate_profile = {
        "name": beneficiary.get("name"),
        "trade": responses.get("workInterest") or beneficiary.get("current_occupation") or "",
        "workInterest": responses.get("workInterest") or beneficiary.get("current_occupation") or "",
        "education": responses.get("education") or beneficiary.get("education_level") or "",
        "mobility": responses.get("mobility") or beneficiary.get("mobility_preference") or "",
        "preference": responses.get("preference") or beneficiary.get("primary_goal") or "",
        "goal": responses.get("preference") or beneficiary.get("primary_goal") or "",
        "state_id": state_id,
        "district_id": district_id,
        "age": beneficiary.get("age"),
    }

    # 4. Fetch Active Opportunities
    opp_query = client.table("opportunities").select("*")
    try:
        opp_res = opp_query.eq("active", True).execute()
        opp_rows = _rows(opp_res)
    except Exception:
        # Backward compatibility if active column is not indexed/available
        opp_res = opp_query.execute()
        opp_rows = _rows(opp_res)

    if not opp_rows:
        return RecommendationResponseContract(
            beneficiary_id=beneficiary_id,
            state_id=state_id,
            district_id=district_id,
            interview_id=interview_id,
            has_completed_interview=True,
            generated_at=_now(),
            message="No active opportunities currently available in the catalog.",
            recommendations=[],
            ineligible_opportunities=[],
        )

    # 5. Fetch Mapped Skills Metadata
    skills_by_opp: dict[str, list[RecommendationSkillMetadata]] = {}
    try:
        skills_res = client.table("opportunity_skills").select(
            "opportunity_id, skill_id, is_taught, priority, skills(id, name, sector, nsqf_level, qp_code)"
        ).execute()

        for item in _rows(skills_res):
            opp_id = item.get("opportunity_id")
            if not opp_id:
                continue

            skill_obj = item.get("skills")
            if isinstance(skill_obj, dict):
                metadata = RecommendationSkillMetadata(
                    id=skill_obj["id"],
                    name=skill_obj["name"],
                    sector=skill_obj.get("sector"),
                    nsqf_level=skill_obj.get("nsqf_level"),
                    qp_code=skill_obj.get("qp_code"),
                    is_taught=item.get("is_taught", True),
                )
                skills_by_opp.setdefault(opp_id, []).append(metadata)
            elif item.get("skill_id"):
                # Relation not expanded, look up directly or store minimal
                skills_by_opp.setdefault(opp_id, []).append(
                    RecommendationSkillMetadata(
                        id=str(item["skill_id"]),
                        name=str(item["skill_id"]),
                        is_taught=item.get("is_taught", True),
                    )
                )
    except Exception:
        logger.warning("Could not pre-fetch mapped skills for recommendations")

    # 6. Evaluate Eligibility & Calculate Scores Deterministically
    eligible_list: list[RecommendationResultContract] = []
    ineligible_list: list[RecommendationResultContract] = []

    for opp in opp_rows:
        opp_id = opp["id"]
        is_eligible, matched_crit, unmet_crit = check_hard_eligibility(candidate_profile, opp)
        mapped_skills = skills_by_opp.get(opp_id, [])

        if is_eligible:
            score, scoring_reasons = calculate_match_score(candidate_profile, opp)
            result = RecommendationResultContract(
                opportunity_id=opp_id,
                title=opp.get("title"),
                eligible=True,
                score=score,
                matched_criteria=matched_crit,
                unmet_criteria=[],
                reasons=scoring_reasons + matched_crit,
                state_id=opp.get("state_id"),
                district_id=opp.get("district_id"),
                nsqf_level=opp.get("nsqf_level"),
                qp_code=opp.get("qp_code"),
                skills=mapped_skills,
            )
            eligible_list.append(result)
        else:
            result = RecommendationResultContract(
                opportunity_id=opp_id,
                title=opp.get("title"),
                eligible=False,
                score=0,
                matched_criteria=matched_crit,
                unmet_criteria=unmet_crit,
                reasons=unmet_crit,
                state_id=opp.get("state_id"),
                district_id=opp.get("district_id"),
                nsqf_level=opp.get("nsqf_level"),
                qp_code=opp.get("qp_code"),
                skills=mapped_skills,
            )
            ineligible_list.append(result)

    # 7. Deterministic Sorting
    # Primary: score DESC
    # Secondary tie-breaker: nsqf_level DESC (higher NSQF qualification prioritized)
    # Tertiary tie-breaker: opportunity_id ASC (guarantees 100% reproducible ordering)
    eligible_list.sort(
        key=lambda r: (-r.score, -(r.nsqf_level or 0), r.opportunity_id)
    )

    ineligible_list.sort(
        key=lambda r: r.opportunity_id
    )

    return RecommendationResponseContract(
        beneficiary_id=beneficiary_id,
        state_id=state_id,
        district_id=district_id,
        interview_id=interview_id,
        has_completed_interview=True,
        generated_at=_now(),
        message=f"Generated {len(eligible_list)} personalized recommendation(s) based on your verified profile.",
        recommendations=eligible_list,
        ineligible_opportunities=ineligible_list,
    )
