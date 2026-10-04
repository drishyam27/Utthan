"""
Utthan Backend - Recommendation Engine 2.0 Service Layer.
Authoritative NSQF/NQR Catalog Course Recommendations with Deterministic Eligibility and Explainable Ranking.
Zero LLM hallucination in eligibility or course selection.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from supabase import Client

from app.schemas.adaptive_interview import (
    NSQFCompetencyEvidence,
    StructuredBeneficiaryProfile,
)
from app.schemas.nsqf_recommendation import (
    NSQFEligibilityEvaluation,
    NSQFEligibilityStatus,
    NSQFRecommendationItem,
    NSQFRecommendationResponse,
)
from app.services.adaptive_interview_service import (
    _load_beneficiary_row,
    _load_interview_row,
    get_or_initialize_profile,
)
from app.services.nsqf_ingestion import EXCLUDED_SECTORS, slugify
from app.services.nsqf_service import _get_in_memory_catalog

logger = logging.getLogger("utthan.nsqf_recommendation")

# Canonical Education Ranks for Deterministic Minimum-Threshold Checks
EDUCATION_RANK_MAP: Dict[str, int] = {
    "none": 0,
    "no_formal": 1,
    "literate_read_write": 2,
    "5th": 3,
    "6th": 4,
    "7th": 5,
    "8th": 6,
    "9th": 7,
    "10th": 8,
    "11th": 9,
    "12th": 10,
    "1st_year_diploma": 11,
    "ug_diploma": 12,
    "diploma": 13,
    "ug": 14,
    "graduate": 15,
    "post_graduate": 16,
    "phd": 17,
    "previous_nsqf": 8,
    "iti_instructor_cits": 13,
}

# 8 Official Notional Hours Buckets
ORDERED_HOURS_BUCKETS = [
    "1–200",
    "201–400",
    "401–600",
    "601–800",
    "801–1000",
    "1001–1200",
    "1201–2400",
    "Above 2401",
]

STOP_WORDS: Set[str] = {
    "and", "the", "for", "with", "a", "an", "in", "on", "at", "to", "of", "is",
    "are", "or", "by", "as", "be", "from", "that", "which", "this", "level",
    "skills", "course", "training", "qualification", "job", "role", "work",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def extract_keywords(text: Optional[str]) -> Set[str]:
    """Extracts substantive lowercase keywords from text."""
    if not text:
        return set()
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text).lower())
    words = [w for w in cleaned.split() if len(w) > 2 and w not in STOP_WORDS]
    return set(words)


def extract_course_minimum_education(
    desc: Optional[str],
    progression: Optional[str],
) -> Optional[Tuple[str, int]]:
    """
    Extracts explicit minimum education requirement from course text if deterministically present.
    Returns (canonical_edu_str, rank) or None if requirement is not specified.
    """
    combined = f"{desc or ''} {progression or ''}".lower()
    
    # Check for explicit threshold statements
    patterns = [
        (r'(?:minimum|min|at least|eligibility:?|eligibility criteria:?)\s*(?:is\s*)?(?:class\s*|standard\s*|grade\s*)?(10th|class 10|matric)', "10th"),
        (r'(?:minimum|min|at least|eligibility:?|eligibility criteria:?)\s*(?:is\s*)?(?:class\s*|standard\s*|grade\s*)?(12th|class 12|inter|higher secondary|10\+2)', "12th"),
        (r'(?:minimum|min|at least|eligibility:?|eligibility criteria:?)\s*(?:is\s*)?(?:class\s*|standard\s*|grade\s*)?(8th|class 8)', "8th"),
        (r'(?:minimum|min|at least|eligibility:?|eligibility criteria:?)\s*(?:is\s*)?(?:class\s*|standard\s*|grade\s*)?(5th|class 5)', "5th"),
        (r'(?:minimum|min|at least|eligibility:?|eligibility criteria:?)\s*(?:is\s*)?(?:graduate|degree|bachelor)', "graduate"),
        (r'(?:minimum|min|at least|eligibility:?|eligibility criteria:?)\s*(?:is\s*)?(?:diploma|polytechnic)', "diploma"),
    ]

    for pat, edu_key in patterns:
        if re.search(pat, combined):
            return edu_key, EDUCATION_RANK_MAP.get(edu_key, 8)

    return None


def evaluate_nsqf_eligibility(
    profile: StructuredBeneficiaryProfile,
    qualification: Dict[str, Any],
) -> NSQFEligibilityEvaluation:
    """
    Deterministically evaluates candidate eligibility against an authoritative NSQF qualification.
    Follows strict safety rules: zero guessing, records unavailable requirements explicitly.
    """
    hard_failures: List[str] = []
    warnings: List[str] = []
    matched_requirements: List[str] = []
    unavailable_requirements: List[str] = []

    # 1. HARD SAFETY RULE: Excluded Sectors Gate (Zero Tolerance)
    sector_name = qualification.get("sector_name") or ""
    sector_id = qualification.get("sector_id") or ""
    if sector_name in EXCLUDED_SECTORS or any(slugify(ex) == sector_id for ex in EXCLUDED_SECTORS):
        hard_failures.append(f"Sector '{sector_name}' is on the statutory excluded list and prohibited from recommendation.")
        return NSQFEligibilityEvaluation(
            status=NSQFEligibilityStatus.NOT_ELIGIBLE,
            eligible=False,
            hard_failures=hard_failures,
            warnings=warnings,
            matched_requirements=matched_requirements,
            unavailable_requirements=unavailable_requirements,
        )

    # 2. PwD Compatibility Gate
    is_course_pwd = qualification.get("is_pwd", False)
    course_pwd_cats = qualification.get("pwd_categories") or []
    
    if profile.pwd_status:
        user_cats = profile.pwd_categories or []
        if is_course_pwd:
            if course_pwd_cats and user_cats:
                # Check category intersection
                matching_cats = [c for c in user_cats if c in course_pwd_cats]
                if matching_cats:
                    matched_requirements.append(
                        f"PwD category alignment verified: course specifically tailored for {', '.join(matching_cats)}"
                    )
                else:
                    # Course tailored specifically for a different disability (e.g., VI vs LD)
                    # Safe handling: add warning rather than silent pass if exclusively tagged
                    warnings.append(
                        f"Course is tailored for PwD categories {course_pwd_cats}, while beneficiary profile lists {user_cats}."
                    )
            else:
                matched_requirements.append("Course includes specialized PwD accessibility/curriculum tailoring")
        else:
            warnings.append("General NSQF course; field verify center-level disability accommodations before enrollment")
    else:
        if is_course_pwd:
            # If beneficiary is not PwD, specialized PwD courses (especially SCPwD) are prioritized for PwD citizens
            if course_pwd_cats:
                warnings.append("Course includes specialized disability training aids intended primarily for PwD learners")

    # 3. Minimum Education Check (Only when explicitly supported by catalog data)
    extracted_edu = extract_course_minimum_education(
        qualification.get("description"),
        qualification.get("progression_pathway"),
    )
    if extracted_edu:
        req_edu, req_rank = extracted_edu
        user_edu = profile.education or "none"
        user_rank = EDUCATION_RANK_MAP.get(user_edu, 0)
        
        if user_rank >= req_rank:
            matched_requirements.append(
                f"Education qualification satisfied: required {req_edu.replace('_', ' ')}, candidate possesses {user_edu.replace('_', ' ')}"
            )
        else:
            hard_failures.append(
                f"Education prerequisite not met: course indicates minimum {req_edu.replace('_', ' ')} (candidate has {user_edu.replace('_', ' ')})"
            )
    else:
        unavailable_requirements.append("Minimum entry education threshold not recorded in catalog metadata")

    # 4. Vocational Training Requirement
    # NSQF catalog qualifications are mostly entry/dual track unless specifically advanced
    if qualification.get("qualification_type") in ("Apprenticeship", "CITS"):
        if qualification.get("qualification_type") == "CITS" and not profile.vocational_training:
            hard_failures.append("Craft Instructor Training Scheme (CITS) requires prior vocational certification (NTC/NAC/Diploma)")
        else:
            if profile.vocational_training:
                matched_requirements.append(f"Prior vocational training ({profile.vocational_training_type}) satisfies entry requirement")
    else:
        unavailable_requirements.append("Specific vocational pre-requisite not mandatory in catalog metadata")

    # 5. Experience Prerequisite
    # Most NSQF qualifications do not have strict minimum experience gates unless supervisory (level >= 6)
    nsqf_level = float(qualification.get("nsqf_level") or 1.0)
    if nsqf_level >= 6.0 and profile.work_experience_years < 1.0:
        warnings.append(f"NSQF Level {nsqf_level} typically assumes industry experience or supervisory foundation")
    else:
        unavailable_requirements.append("Experience threshold not strictly enforced by catalog metadata")

    # Final Eligibility Status
    is_eligible = len(hard_failures) == 0
    status = NSQFEligibilityStatus.ELIGIBLE if is_eligible else NSQFEligibilityStatus.NOT_ELIGIBLE

    return NSQFEligibilityEvaluation(
        status=status,
        eligible=is_eligible,
        hard_failures=hard_failures,
        warnings=warnings,
        matched_requirements=matched_requirements,
        unavailable_requirements=unavailable_requirements,
    )


def calculate_nsqf_relevance_score(
    profile: StructuredBeneficiaryProfile,
    qualification: Dict[str, Any],
) -> Tuple[int, List[str]]:
    """
    Computes deterministic, explainable relevance score (0-100) based on:
    - Sector alignment (max 35)
    - Competency & skill evidence (max 25)
    - Capacity / notional hours fit (max 15)
    - PwD compatibility (max 10)
    - Education & vocational background (max 10)
    - NSQF level & progression relevance (max 5)
    """
    score = 0
    reasons: List[str] = []

    # 1. Sector Alignment (Max 35 points)
    q_sector_id = qualification.get("sector_id") or ""
    q_sector_name = qualification.get("sector_name") or ""
    prof_sector_id = profile.interested_sector_id or ""
    prof_sector_name = profile.interested_sector_name or ""

    if prof_sector_id and (q_sector_id == prof_sector_id or slugify(q_sector_name) == prof_sector_id):
        score += 35
        reasons.append(f"Direct match with your chosen sector ({q_sector_name})")
    elif prof_sector_name and prof_sector_name.lower() in q_sector_name.lower():
        score += 30
        reasons.append(f"Strongly aligned with your preferred industry area ({q_sector_name})")
    else:
        # Cross-sector baseline
        score += 10
        reasons.append(f"Curriculum offers transferable foundation skills in {q_sector_name}")

    # 2. Competency & Skill Evidence (Max 25 points)
    # Collect all user evidence tokens
    user_tokens: Set[str] = set()
    user_tokens.update(extract_keywords(profile.current_occupation))
    for s in profile.skills:
        user_tokens.update(extract_keywords(s))
    for c in profile.competencies:
        user_tokens.update(extract_keywords(c))
    for t in profile.tools_familiarity:
        user_tokens.update(extract_keywords(t))

    ev = profile.competency_evidence
    if ev:
        for item in ev.professional_knowledge:
            user_tokens.update(extract_keywords(item))
        for item in ev.technical_skills:
            user_tokens.update(extract_keywords(item))
        for item in ev.core_skills:
            user_tokens.update(extract_keywords(item))
        for item in ev.process_capability:
            user_tokens.update(extract_keywords(item))

    # Match against qualification text
    q_text = " ".join([
        qualification.get("title") or "",
        qualification.get("proposed_occupation") or "",
        qualification.get("description") or "",
        qualification.get("progression_pathway") or "",
    ])
    q_tokens = extract_keywords(q_text)

    overlap = user_tokens.intersection(q_tokens)
    if overlap:
        # Up to 25 points based on depth of verified evidence overlap
        pts = min(25, max(10, len(overlap) * 5))
        score += pts
        matched_sample = sorted(list(overlap))[:4]
        reasons.append(f"Matches your verified practical competencies and tools: {', '.join(matched_sample)}")
    else:
        score += 5
        reasons.append("Introductory modules suitable for building practical domain competencies")

    # 3. Capacity / Notional Hours Fit (Max 15 points)
    q_range = qualification.get("notional_hours_range")
    prof_range = profile.notional_hours_range

    if prof_range and q_range:
        if prof_range == q_range:
            score += 15
            reasons.append(f"Course duration ({q_range} hours) matches your exact schedule capacity")
        else:
            try:
                prof_idx = ORDERED_HOURS_BUCKETS.index(prof_range)
                q_idx = ORDERED_HOURS_BUCKETS.index(q_range)
                if abs(prof_idx - q_idx) == 1:
                    score += 8
                    reasons.append(f"Course duration ({q_range} hours) is close to your preferred range ({prof_range})")
                else:
                    score += 4
                    reasons.append(f"Flexible duration format ({q_range} hours)")
            except ValueError:
                score += 5
    else:
        score += 10
        if q_range:
            reasons.append(f"Standard curriculum duration ({q_range} hours)")

    # 4. PwD Compatibility (Max 10 points)
    if profile.pwd_status:
        if qualification.get("is_pwd"):
            score += 10
            reasons.append("Specialized disability-inclusive curriculum and assessment methods")
        else:
            score += 5
            reasons.append("Standard NSQF curriculum accessible with reasonable training accommodations")
    else:
        score += 10

    # 5. Education & Vocational Background Alignment (Max 10 points)
    user_edu_rank = EDUCATION_RANK_MAP.get(profile.education or "none", 0)
    if user_edu_rank >= 8:  # 10th pass or higher
        score += 6
        reasons.append("Candidate academic foundation meets standard vocational prerequisites")
    elif user_edu_rank >= 6:  # 8th pass
        score += 4
        reasons.append("Accessible learning curve for candidates with middle school education")
    else:
        score += 3
        reasons.append("Practical, hands-on curriculum accessible without extensive formal schooling")

    if profile.vocational_training:
        score += 4
        reasons.append(f"Builds directly on your prior vocational training ({profile.vocational_training_type or 'technical'})")

    # 6. NSQF Level & Experience Progression Fit (Max 5 points)
    lvl = float(qualification.get("nsqf_level") or 1.0)
    exp = profile.work_experience_years

    if exp < 1.0:
        if lvl <= 3.5:
            score += 5
            reasons.append(f"NSQF Level {lvl} is ideal for job-seekers starting in this trade")
        else:
            score += 2
    elif 1.0 <= exp <= 3.0:
        if 3.0 <= lvl <= 4.5:
            score += 5
            reasons.append(f"NSQF Level {lvl} aligns with your {exp} year(s) of practical experience")
        else:
            score += 3
    else:  # > 3 years
        if lvl >= 4.0:
            score += 5
            reasons.append(f"NSQF Level {lvl} supports formal career progression for experienced practitioners")
        else:
            score += 2

    final_score = min(100, max(0, score))
    return final_score, reasons


def check_insufficient_profile(profile: StructuredBeneficiaryProfile) -> Tuple[bool, List[str]]:
    """
    Checks if beneficiary profile has sufficient information to generate responsible recommendations.
    Returns (is_insufficient, missing_field_names).
    """
    missing: List[str] = []

    # Must have chosen a sector or provided substantial competency/trade evidence
    has_sector = bool(profile.interested_sector_id or profile.interested_sector_name)
    has_trade = bool(profile.current_occupation)
    has_skills = bool(profile.skills or profile.competencies or profile.tools_familiarity)
    
    if not has_sector and not has_trade and not has_skills:
        missing.append("interested_sector")

    # Education should be collected
    if not profile.education:
        missing.append("education")

    # Overall completeness threshold
    if profile.completeness_percentage < 15 and len(missing) > 0:
        return True, missing

    return len(missing) >= 2, missing


def load_candidate_qualifications(
    client: Optional[Client],
    profile: StructuredBeneficiaryProfile,
) -> List[Dict[str, Any]]:
    """
    Loads authoritative qualification candidates from Supabase or cached catalog.
    Pre-filters by sector to optimize performance where possible, excluding forbidden sectors.
    """
    target_sector_id = profile.interested_sector_id
    if target_sector_id:
        target_sector_id = target_sector_id.lower().strip()

    # 1. Try Supabase if available
    if client is not None:
        try:
            query = client.table("nsqf_qualifications").select("*").eq("is_active", True)
            if target_sector_id:
                query = query.eq("sector_id", target_sector_id)
            res = query.limit(200).execute()
            rows = getattr(res, "data", [])
            if rows is not None:
                safe_rows = [r for r in rows if r.get("sector_name") not in EXCLUDED_SECTORS]
                # If a specific sector was requested, return the results for that sector (even if empty)
                if target_sector_id:
                    return safe_rows
                if safe_rows:
                    return safe_rows
        except Exception as exc:
            logger.warning("Supabase qualification query failed (%s); falling back to authoritative local catalog", exc)

    # 2. Local Authoritative Catalog Fallback
    _, all_courses, _ = _get_in_memory_catalog()
    
    # Filter out excluded sectors
    safe_courses = [
        c for c in all_courses
        if c.get("sector_name") not in EXCLUDED_SECTORS
        and c.get("sector_id") not in [slugify(ex) for ex in EXCLUDED_SECTORS]
    ]

    if target_sector_id or profile.interested_sector_name:
        sector_matched = [
            c for c in safe_courses
            if (target_sector_id and c.get("sector_id") == target_sector_id)
            or (profile.interested_sector_name and c.get("sector_name", "").lower() == profile.interested_sector_name.lower())
        ]
        return sector_matched

    return safe_courses


def generate_nsqf_recommendations(
    client: Optional[Client],
    profile: StructuredBeneficiaryProfile,
    limit: int = 15,
) -> NSQFRecommendationResponse:
    """
    Generates deterministic, explainable recommendations from the authoritative NSQF/NQR catalog.
    """
    b_id = profile.beneficiary_id
    i_id = profile.interview_id
    now = _now()

    # 1. Check for Insufficient Profile
    is_insufficient, missing_fields = check_insufficient_profile(profile)
    if is_insufficient:
        return NSQFRecommendationResponse(
            beneficiary_id=b_id,
            interview_id=i_id,
            status="insufficient_profile",
            generated_at=now,
            total_evaluated=0,
            total_recommended=0,
            missing_profile_fields=missing_fields,
            recommendations=[],
            ineligible_sample=[],
            message=(
                f"Your profile requires additional information before courses can be recommended. "
                f"Missing: {', '.join(missing_fields).replace('_', ' ')}."
            ),
        )

    # 2. Load candidate qualifications from authoritative catalog
    catalog_courses = load_candidate_qualifications(client, profile)
    if not catalog_courses:
        return NSQFRecommendationResponse(
            beneficiary_id=b_id,
            interview_id=i_id,
            status="no_match",
            generated_at=now,
            total_evaluated=0,
            total_recommended=0,
            missing_profile_fields=[],
            recommendations=[],
            ineligible_sample=[],
            message="No active NSQF qualifications currently available matching the requested sector criteria.",
        )

    # 3. Evaluate Eligibility & Calculate Deterministic Relevance
    eligible_items: List[NSQFRecommendationItem] = []
    ineligible_items: List[NSQFRecommendationItem] = []

    for c in catalog_courses:
        # Enforce server-side excluded sectors strictly
        s_name = c.get("sector_name") or ""
        if s_name in EXCLUDED_SECTORS or slugify(s_name) in [slugify(ex) for ex in EXCLUDED_SECTORS]:
            continue

        evaluation = evaluate_nsqf_eligibility(profile, c)
        score, reasons = calculate_nsqf_relevance_score(profile, c)

        item = NSQFRecommendationItem(
            q_code=c.get("q_code") or f"NSQF-{c.get('id', 'unknown')}",
            title=c.get("title") or "NSQF Course",
            sector_id=c.get("sector_id") or "general",
            sector_name=c.get("sector_name") or "General",
            nsqf_level=float(c.get("nsqf_level") or 1.0),
            qualification_type=c.get("qualification_type"),
            notional_hours_range=c.get("notional_hours_range"),
            min_notional_hours=c.get("min_notional_hours"),
            max_notional_hours=c.get("max_notional_hours"),
            is_pwd=bool(c.get("is_pwd")),
            pwd_categories=c.get("pwd_categories") or [],
            awarding_body=c.get("awarding_body"),
            proposed_occupation=c.get("proposed_occupation"),
            progression_pathway=c.get("progression_pathway"),
            description=c.get("description"),
            score=score,
            rank=1,  # Rank will be computed after deterministic sorting
            eligibility=evaluation,
            match_reasons=reasons + evaluation.matched_requirements,
            warnings=evaluation.warnings,
            source="nsqf_nqr_catalog",
        )

        if evaluation.eligible:
            eligible_items.append(item)
        else:
            ineligible_items.append(item)

    # 4. Deterministic Ranking
    # Sort criteria:
    # 1. score DESC
    # 2. nsqf_level DESC
    # 3. q_code ASC (100% reproducible tie-breaker)
    eligible_items.sort(
        key=lambda x: (-x.score, -x.nsqf_level, x.q_code)
    )

    # Assign 1-indexed ranks
    for rank_idx, item in enumerate(eligible_items, start=1):
        item.rank = rank_idx

    final_recommendations = eligible_items[:limit]

    # Deterministic Ineligible Sample
    ineligible_items.sort(key=lambda x: x.q_code)
    ineligible_sample = ineligible_items[:5]

    # Handle No-Match
    if not final_recommendations:
        return NSQFRecommendationResponse(
            beneficiary_id=b_id,
            interview_id=i_id,
            status="no_match",
            generated_at=now,
            total_evaluated=len(catalog_courses),
            total_recommended=0,
            missing_profile_fields=[],
            recommendations=[],
            ineligible_sample=ineligible_sample,
            message="No qualifications passed deterministic eligibility criteria for the current profile parameters.",
        )

    return NSQFRecommendationResponse(
        beneficiary_id=b_id,
        interview_id=i_id,
        status="eligible",
        generated_at=now,
        total_evaluated=len(catalog_courses),
        total_recommended=len(eligible_items),
        missing_profile_fields=[],
        recommendations=final_recommendations,
        ineligible_sample=ineligible_sample,
        message=f"Deterministically matched {len(eligible_items)} authoritative NSQF/NQR course(s) from official catalog.",
    )


def generate_nsqf_recommendations_for_beneficiary(
    client: Client,
    beneficiary_id: UUID,
    interview_id: Optional[UUID] = None,
    limit: int = 15,
) -> NSQFRecommendationResponse:
    """
    Convenience function to resolve beneficiary and interview data,
    construct the StructuredBeneficiaryProfile, and run Recommendation Engine 2.0.
    """
    # 1. Fetch Beneficiary
    b_res = client.table("beneficiaries").select("*").eq("id", str(beneficiary_id)).limit(1).execute()
    b_rows = getattr(b_res, "data", [])
    if not b_rows:
        from app.services.beneficiary_service import BeneficiaryNotFoundError
        raise BeneficiaryNotFoundError(f"Beneficiary {beneficiary_id} not found.")
    b_row = b_rows[0]

    # 2. Fetch Interview (completed or latest in-progress)
    i_row: Dict[str, Any] = {}
    if interview_id:
        i_res = client.table("interview_sessions").select("*").eq("id", str(interview_id)).limit(1).execute()
        i_rows = getattr(i_res, "data", [])
        if i_rows:
            i_row = i_rows[0]

    if not i_row:
        # Check completed sessions first
        i_res = (
            client.table("interview_sessions")
            .select("*")
            .eq("beneficiary_id", str(beneficiary_id))
            .eq("status", "completed")
            .order("completed_at", desc=True)
            .limit(1)
            .execute()
        )
        i_rows = getattr(i_res, "data", [])
        if i_rows:
            i_row = i_rows[0]
        else:
            # Check draft / in-progress
            i_res = (
                client.table("interview_sessions")
                .select("*")
                .eq("beneficiary_id", str(beneficiary_id))
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            i_rows = getattr(i_res, "data", [])
            if i_rows:
                i_row = i_rows[0]

    if not i_row:
        # Create a synthetic placeholder interview row for candidate resolution
        i_row = {
            "id": str(interview_id or UUID("00000000-0000-0000-0000-000000000000")),
            "beneficiary_id": str(beneficiary_id),
            "language": b_row.get("preferred_language", "hi"),
            "extracted_profile": {},
            "responses": {},
        }
    else:
        if "beneficiary_id" not in i_row:
            i_row["beneficiary_id"] = str(beneficiary_id)
        if "id" not in i_row:
            i_row["id"] = str(interview_id or UUID("00000000-0000-0000-0000-000000000000"))


    # 3. Construct Phase 3B StructuredBeneficiaryProfile
    profile = get_or_initialize_profile(i_row, b_row)

    # 4. Generate Authoritative NSQF Recommendations
    return generate_nsqf_recommendations(client, profile, limit=limit)
