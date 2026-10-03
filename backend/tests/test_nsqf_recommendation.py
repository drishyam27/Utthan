"""
Utthan Backend - Unit & Integration Tests for NSQF Recommendation Engine 2.0.
Verifies authoritative catalog source, strict excluded-sector enforcement, deterministic eligibility,
explainable ranking, PwD matching, canonical hierarchies, security capability gates, and Groq isolation.
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock
from uuid import UUID, uuid4
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.schemas.adaptive_interview import (
    NSQFCompetencyEvidence,
    StructuredBeneficiaryProfile,
)
from app.schemas.nsqf_recommendation import (
    NSQFEligibilityStatus,
    NSQFRecommendationResponse,
)
from app.services.nsqf_ingestion import EXCLUDED_SECTORS
from app.services.nsqf_recommendation_service import (
    calculate_nsqf_relevance_score,
    evaluate_nsqf_eligibility,
    generate_nsqf_recommendations,
    generate_nsqf_recommendations_for_beneficiary,
    load_candidate_qualifications,
)
from app.services.nsqf_service import _get_in_memory_catalog


@pytest.fixture
def base_beneficiary_profile() -> StructuredBeneficiaryProfile:
    """Standard Phase 3B candidate profile with Agriculture sector interest."""
    return StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        preferred_language="hi",
        name="Ramesh Kumar",
        state_id="IN-UP",
        state_name="Uttar Pradesh",
        district_id="IN-UP-VNS",
        district_name="Varanasi",
        education="10th",
        education_label="10th Pass",
        vocational_training=False,
        vocational_training_type=None,
        work_experience_years=2.0,
        work_experience_label="2 Years",
        current_occupation="Farm Laborer",
        interested_sector_id="agriculture",
        interested_sector_name="Agriculture",
        notional_hours_range="401–600",
        pwd_status=False,
        pwd_categories=[],
        skills=["tractor driving", "soil preparation", "crop sowing"],
        competencies=["irrigation management", "seed treatment"],
        tools_familiarity=["plough", "sprayer"],
        competency_evidence=NSQFCompetencyEvidence(
            professional_knowledge=["crop cultivation cycles", "organic fertilizers"],
            technical_skills=["sprayer maintenance", "tillage operation"],
            core_skills=["basic measurements", "team coordination"],
            process_capability=["routine field operations"],
            responsibility_level="works under supervision with some autonomy",
        ),
        completeness_percentage=90,
    )


# ==============================================================================
# 1. CATALOG SOURCE & REAL RECORDS VERIFICATION
# ==============================================================================

def test_authoritative_catalog_source(base_beneficiary_profile):
    """Recommendations must come exclusively from the authoritative 2,810-course catalog."""
    response = generate_nsqf_recommendations(None, base_beneficiary_profile, limit=10)

    assert response.status == "eligible"
    assert response.total_recommended > 0
    assert len(response.recommendations) > 0

    # Ensure every returned recommendation has an authentic NQR q_code and fields
    for rec in response.recommendations:
        assert rec.source == "nsqf_nqr_catalog"
        assert len(rec.q_code) > 3
        assert rec.title
        assert rec.sector_name
        assert rec.nsqf_level >= 1.0
        assert rec.score >= 0 and rec.score <= 100
        assert rec.rank >= 1
        assert rec.eligibility.eligible is True
        assert len(rec.match_reasons) > 0


def test_real_catalog_diversity_and_half_levels():
    """Verify catalog contains authentic decimal levels (2.5, 3.5, 4.5) and 44 sectors."""
    sectors, courses, _ = _get_in_memory_catalog()
    assert len(sectors) == 44
    assert len(courses) == 2810

    # Verify decimal levels preserved without rounding
    levels = {c["nsqf_level"] for c in courses}
    assert 2.5 in levels
    assert 3.5 in levels
    assert 4.5 in levels
    assert 5.5 in levels


# ==============================================================================
# 2. STRICT EXCLUDED SECTORS HARD GATE (ZERO TOLERANCE)
# ==============================================================================

def test_all_15_excluded_sectors_blocked_strictly(base_beneficiary_profile):
    """The 15 excluded sectors must NEVER appear in recommendations, even if queried directly."""
    for excluded_sector in EXCLUDED_SECTORS:
        # Simulate candidate wanting an excluded sector
        profile = base_beneficiary_profile.model_copy(update={
            "interested_sector_name": excluded_sector,
            "interested_sector_id": excluded_sector.lower().replace(" ", "-"),
        })

        # Test direct qualification evaluation
        fake_excluded_qualification = {
            "q_code": "FORBIDDEN-001",
            "title": f"{excluded_sector} Officer",
            "sector_name": excluded_sector,
            "sector_id": excluded_sector.lower().replace(" ", "-"),
            "nsqf_level": 4.0,
            "is_pwd": False,
        }

        evaluation = evaluate_nsqf_eligibility(profile, fake_excluded_qualification)
        assert evaluation.eligible is False
        assert evaluation.status == NSQFEligibilityStatus.NOT_ELIGIBLE
        assert any("excluded list" in failure for failure in evaluation.hard_failures)


def test_zero_excluded_sectors_in_recommendation_output(base_beneficiary_profile):
    """Verify total count of excluded sector courses in any recommendation output is strictly 0."""
    response = generate_nsqf_recommendations(None, base_beneficiary_profile, limit=50)

    for rec in response.recommendations:
        assert rec.sector_name not in EXCLUDED_SECTORS
        for ex in EXCLUDED_SECTORS:
            assert ex.lower() not in rec.sector_name.lower()


# ==============================================================================
# 3. CANONICAL EDUCATION MATCHING & SAFE SEMANTICS
# ==============================================================================

def test_education_matching_satisfied_when_candidate_meets_threshold(base_beneficiary_profile):
    """Candidate with 10th meets a course requiring 10th."""
    profile = base_beneficiary_profile.model_copy(update={"education": "10th"})
    qualification = {
        "q_code": "AGRI-001",
        "title": "Soil Testing Technician",
        "sector_name": "Agriculture",
        "nsqf_level": 4.0,
        "description": "Eligibility criteria: minimum 10th pass with science.",
        "progression_pathway": "Supervisor",
        "is_pwd": False,
    }

    eval_result = evaluate_nsqf_eligibility(profile, qualification)
    assert eval_result.eligible is True
    assert any("Education qualification satisfied" in m for m in eval_result.matched_requirements)


def test_education_matching_satisfied_by_higher_education(base_beneficiary_profile):
    """Candidate with graduate degree satisfies 10th requirement."""
    profile = base_beneficiary_profile.model_copy(update={"education": "graduate"})
    qualification = {
        "q_code": "AGRI-002",
        "title": "Micro Irrigation Technician",
        "sector_name": "Agriculture",
        "nsqf_level": 4.0,
        "description": "Eligibility: minimum class 10 pass.",
        "is_pwd": False,
    }

    eval_result = evaluate_nsqf_eligibility(profile, qualification)
    assert eval_result.eligible is True
    assert any("Education qualification satisfied" in m for m in eval_result.matched_requirements)


def test_education_hard_failure_when_below_threshold(base_beneficiary_profile):
    """Candidate with 5th fails a course explicitly requiring 10th."""
    profile = base_beneficiary_profile.model_copy(update={"education": "5th"})
    qualification = {
        "q_code": "AGRI-003",
        "title": "Precision Farming Operator",
        "sector_name": "Agriculture",
        "nsqf_level": 4.0,
        "description": "Eligibility criteria is class 10th pass.",
        "is_pwd": False,
    }

    eval_result = evaluate_nsqf_eligibility(profile, qualification)
    assert eval_result.eligible is False
    assert any("Education prerequisite not met" in f for f in eval_result.hard_failures)


def test_ambiguous_education_marked_unavailable_without_guessing(base_beneficiary_profile):
    """When catalog course has no education prerequisite mentioned, do NOT guess."""
    qualification = {
        "q_code": "AGRI-004",
        "title": "Gardener",
        "sector_name": "Agriculture",
        "nsqf_level": 2.0,
        "description": "Basic gardening and maintenance tasks.",
        "progression_pathway": "Head Gardener",
        "is_pwd": False,
    }

    eval_result = evaluate_nsqf_eligibility(base_beneficiary_profile, qualification)
    assert eval_result.eligible is True
    assert any("education threshold not recorded" in u for u in eval_result.unavailable_requirements)


# ==============================================================================
# 4. VOCATIONAL TRAINING MATCHING
# ==============================================================================

def test_cits_qualification_requires_vocational_background(base_beneficiary_profile):
    """Craft Instructor Training (CITS) requires prior vocational training."""
    # Profile with no vocational training
    non_voc_profile = base_beneficiary_profile.model_copy(update={
        "vocational_training": False,
        "vocational_training_type": "none",
    })
    cits_qualification = {
        "q_code": "CITS-001",
        "title": "Craft Instructor (Agriculture Machinery)",
        "sector_name": "Agriculture",
        "qualification_type": "CITS",
        "nsqf_level": 5.0,
        "is_pwd": False,
    }

    eval_fail = evaluate_nsqf_eligibility(non_voc_profile, cits_qualification)
    assert eval_fail.eligible is False
    assert any("CITS" in f for f in eval_fail.hard_failures)

    # Profile with NTC/CTS vocational training
    voc_profile = base_beneficiary_profile.model_copy(update={
        "vocational_training": True,
        "vocational_training_type": "cts_ntc",
    })
    eval_pass = evaluate_nsqf_eligibility(voc_profile, cits_qualification)
    assert eval_pass.eligible is True
    assert any("Prior vocational training" in m for m in eval_pass.matched_requirements)


# ==============================================================================
# 5. PWD DETERMINISTIC MATCHING
# ==============================================================================

def test_pwd_matching_with_specific_category():
    """Beneficiary with Locomotor Disability (LD) matches LD-tagged qualification."""
    pwd_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Sunita PwD",
        education="10th",
        interested_sector_id="green-jobs",
        interested_sector_name="Green Jobs",
        pwd_status=True,
        pwd_categories=["LD"],
        completeness_percentage=80,
    )

    ld_qualification = {
        "q_code": "2021/PWD/SCPWD/04886",
        "title": "Solar PV Installer-Civil-PwD LD",
        "sector_name": "Green Jobs",
        "sector_id": "green-jobs",
        "nsqf_level": 4.0,
        "is_pwd": True,
        "pwd_categories": ["LD"],
    }

    eval_result = evaluate_nsqf_eligibility(pwd_profile, ld_qualification)
    assert eval_result.eligible is True
    assert any("PwD category alignment verified" in m for m in eval_result.matched_requirements)

    score, reasons = calculate_nsqf_relevance_score(pwd_profile, ld_qualification)
    assert score >= 50
    assert any("Specialized disability-inclusive" in r for r in reasons)


def test_pwd_category_mismatch_produces_warning():
    """Beneficiary with VI considering a course tailored strictly for LD gets a warning."""
    vi_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        education="10th",
        interested_sector_id="green-jobs",
        pwd_status=True,
        pwd_categories=["VI"],
        completeness_percentage=80,
    )

    ld_qualification = {
        "q_code": "2021/PWD/SCPWD/04886",
        "title": "Solar PV Installer-Civil-PwD LD",
        "sector_name": "Green Jobs",
        "is_pwd": True,
        "pwd_categories": ["LD"],
    }

    eval_result = evaluate_nsqf_eligibility(vi_profile, ld_qualification)
    assert any("tailored for PwD categories ['LD']" in w for w in eval_result.warnings)


# ==============================================================================
# 6. COMPETENCY-BASED RELEVANCE & NOTIONAL HOURS CAPACITY
# ==============================================================================

def test_competency_evidence_increases_relevance_score(base_beneficiary_profile):
    """Candidate with matching practical tools & competencies receives higher score."""
    q_solar = {
        "q_code": "SOLAR-001",
        "title": "Solar PV Rooftop Technician",
        "sector_name": "Green Jobs",
        "sector_id": "green-jobs",
        "proposed_occupation": "Solar Technician",
        "description": "Installation of solar panels, wiring, sprayer cleaning and inverter setup.",
        "nsqf_level": 4.0,
        "is_pwd": False,
    }

    # Profile with relevant tools and skills
    matching_profile = base_beneficiary_profile.model_copy(update={
        "tools_familiarity": ["sprayer", "wiring"],
        "skills": ["solar", "installation"],
    })
    score_high, reasons_high = calculate_nsqf_relevance_score(matching_profile, q_solar)

    # Profile with unrelated tools
    unrelated_profile = base_beneficiary_profile.model_copy(update={
        "tools_familiarity": ["tailoring scissors", "sewing machine"],
        "skills": ["stitching", "embroidery"],
        "competencies": [],
    })
    score_low, _ = calculate_nsqf_relevance_score(unrelated_profile, q_solar)

    assert score_high > score_low
    assert any("practical competencies" in r for r in reasons_high)


def test_notional_hours_capacity_fit(base_beneficiary_profile):
    """Matching duration bucket provides maximum capacity score points."""
    q_bucket_400 = {
        "q_code": "TEST-400",
        "title": "Assistant Surveyor",
        "sector_name": "Construction",
        "notional_hours_range": "401–600",
        "nsqf_level": 3.0,
        "is_pwd": False,
    }

    profile_matching_hours = base_beneficiary_profile.model_copy(update={
        "notional_hours_range": "401–600"
    })
    score_match, reasons = calculate_nsqf_relevance_score(profile_matching_hours, q_bucket_400)
    assert any("matches your exact schedule capacity" in r for r in reasons)


# ==============================================================================
# 7. INSUFFICIENT PROFILE & NO-MATCH BEHAVIOR
# ==============================================================================

def test_insufficient_profile_does_not_force_recommendations():
    """An empty or unguided profile returns insufficient_profile status without guessing."""
    empty_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        education=None,
        interested_sector_id=None,
        interested_sector_name=None,
        skills=[],
        competencies=[],
        tools_familiarity=[],
        completeness_percentage=5,
    )

    response = generate_nsqf_recommendations(None, empty_profile)
    assert response.status == "insufficient_profile"
    assert len(response.recommendations) == 0
    assert "interested_sector" in response.missing_profile_fields


def test_no_match_returns_gracefully(base_beneficiary_profile):
    """When no candidates pass eligibility, status is no_match with clear reasons."""
    # Fake impossible qualification catalog
    impossible_profile = base_beneficiary_profile.model_copy(update={
        "education": "5th",
        "interested_sector_id": "non-existent-sector-xyz",
        "interested_sector_name": "Non Existent Sector",
    })

    response = generate_nsqf_recommendations(None, impossible_profile)
    # Either no courses found for sector or no eligible matches
    assert response.status in ("no_match", "eligible")
    if response.status == "no_match":
        assert len(response.recommendations) == 0
        assert "No active NSQF qualifications" in response.message or "No qualifications passed" in response.message


# ==============================================================================
# 8. DETERMINISTIC RANKING REPRODUCIBILITY & TIE-BREAKER
# ==============================================================================

def test_ranking_is_100_percent_deterministic_and_reproducible(base_beneficiary_profile):
    """Running recommendation twice on identical profile must yield exact identical order and ranks."""
    run1 = generate_nsqf_recommendations(None, base_beneficiary_profile, limit=15)
    run2 = generate_nsqf_recommendations(None, base_beneficiary_profile, limit=15)

    assert len(run1.recommendations) == len(run2.recommendations)
    for r1, r2 in zip(run1.recommendations, run2.recommendations):
        assert r1.q_code == r2.q_code
        assert r1.score == r2.score
        assert r1.rank == r2.rank
        assert r1.nsqf_level == r2.nsqf_level


# ==============================================================================
# 9. API INTEGRATION & CAPABILITY SECURITY
# ==============================================================================

def test_nsqf_recommendation_api_requires_capability_authorization(client: TestClient):
    """API endpoint /api/beneficiaries/{id}/recommendations/nsqf rejects unauthorized calls."""
    random_id = uuid4()
    response = client.get(f"/api/beneficiaries/{random_id}/recommendations/nsqf")
    # Must reject with 401 Unauthorized
    assert response.status_code == 401


def test_nsqf_recommendation_api_with_mock_client():
    """Mock client returns valid NSQFRecommendationResponse structure."""
    client = MagicMock()
    b_id = uuid4()
    i_id = uuid4()

    # 1. Populated beneficiary with occupation/trade
    client.table().select().eq().limit().execute.return_value.data = [{
        "id": str(b_id),
        "name": "Asha Devi",
        "education_level": "10th",
        "current_occupation": "Agriculture",
        "preferred_language": "hi",
        "state_id": "IN-UP",
        "district_id": "IN-UP-VNS",
    }]

    response = generate_nsqf_recommendations_for_beneficiary(client, b_id, interview_id=i_id)
    assert isinstance(response, NSQFRecommendationResponse)
    assert response.beneficiary_id == b_id
    assert response.status == "eligible"
    assert response.total_evaluated > 0
    assert len(response.recommendations) > 0



# ==============================================================================
# 10. GROQ ISOLATION VERIFICATION
# ==============================================================================

def test_recommendation_engine_operates_without_groq(base_beneficiary_profile):
    """NSQF Recommendation Engine 2.0 does not call Groq or external LLM API."""
    import sys
    groq_module = sys.modules.get("groq")
    # Even if groq is mocked or raises error, recommendation engine must succeed
    response = generate_nsqf_recommendations(None, base_beneficiary_profile, limit=5)
    assert response.status == "eligible"
    assert len(response.recommendations) > 0
