"""Focused tests for the Phase 2C-4 deterministic recommendation service."""

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from starlette.testclient import TestClient

from app.db.supabase import get_supabase_client
from app.main import app
from app.schemas.recommendation import RecommendationResponseContract
from app.security.anonymous_session import generate_capability_token, hash_capability_token
from app.services.recommendation_service import (
    calculate_match_score,
    check_hard_eligibility,
    normalize_education,
    normalize_goal,
    normalize_mobility,
)


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.filters = []
        self.limit_value = None
        self.order_column = None
        self.order_desc = False
        self.mode = "select"
        self.payload = None

    def select(self, _columns):
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def order(self, column, desc=False):
        self.order_column = column
        self.order_desc = desc
        return self

    def insert(self, payload):
        self.mode = "insert"
        self.payload = deepcopy(payload)
        return self

    def update(self, payload):
        self.mode = "update"
        self.payload = deepcopy(payload)
        return self

    def _matches(self, row):
        return all(row.get(column) == value for column, value in self.filters)

    def execute(self):
        rows = self.database.get(self.table_name, [])

        if self.mode == "insert":
            row = deepcopy(self.payload)
            row.setdefault("id", str(uuid4()))
            row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            rows.append(row)
            return FakeResponse([deepcopy(row)])

        matching = [row for row in rows if self._matches(row)]
        if self.order_column:
            matching.sort(
                key=lambda row: row.get(self.order_column) or "",
                reverse=self.order_desc,
            )
        if self.limit_value is not None:
            matching = matching[: self.limit_value]

        if self.mode == "update":
            for row in matching:
                row.update(deepcopy(self.payload))
            return FakeResponse([deepcopy(row) for row in matching])

        return FakeResponse([deepcopy(row) for row in matching])


SAMPLE_OPPORTUNITIES = [
    {
        "id": "opp-solar-rooftop",
        "title": "PM Surya Ghar: Rooftop Solar Technician",
        "category": "Green Energy & Renewable",
        "provider": "Ministry of New and Renewable Energy",
        "source": "PM Surya Ghar Portal",
        "source_url": "https://pmsuryaghar.gov.in",
        "state_id": None,
        "district_id": None,
        "education_min": "10th_pass",
        "age_min": 18,
        "age_max": 35,
        "mobility_requirement": "within_15km",
        "primary_goal_fit": "training_stipend",
        "target_trade_keywords": ["solar", "electrical", "maintenance", "solar rooftop"],
        "eligibility_rules": {"panIndia": True, "minEducation": "10th_pass"},
        "nsqf_level": 4,
        "qp_code": "SGJ/Q0101",
        "active": True,
    },
    {
        "id": "opp-pm-ajay-handloom-varanasi",
        "title": "PM-AJAY GIA: Handloom Cluster Development",
        "category": "Traditional Craft & Textiles",
        "provider": "Ministry of Social Justice & Empowerment",
        "source": "PM-AJAY Official Portal",
        "source_url": "https://pmajay.gov.in",
        "state_id": "state-up",
        "district_id": "dist-up-varanasi",
        "education_min": "no_formal",
        "age_min": 18,
        "age_max": None,
        "mobility_requirement": "village_block",
        "primary_goal_fit": "micro_business",
        "target_trade_keywords": ["weaving", "handloom", "textile", "craft"],
        "eligibility_rules": {"panIndia": False},
        "nsqf_level": 4,
        "qp_code": "TSC/Q7301",
        "active": True,
    },
    {
        "id": "opp-kisan-drone-pilot",
        "title": "Kisan Drone Pilot Certification",
        "category": "Agri-Tech & Modern Farming",
        "provider": "Ministry of Agriculture & Farmers Welfare",
        "source": "Kisan Drone Scheme",
        "source_url": "https://agricoop.nic.in",
        "state_id": None,
        "district_id": None,
        "education_min": "10th_pass",
        "age_min": 18,
        "age_max": 45,
        "mobility_requirement": "district_wide",
        "primary_goal_fit": "job_placement",
        "target_trade_keywords": ["drone", "agriculture", "drone pilot", "spraying"],
        "eligibility_rules": {"panIndia": True, "minEducation": "10th_pass"},
        "nsqf_level": 4,
        "qp_code": "AGR/Q1201",
        "active": True,
    },
]

SAMPLE_OPPORTUNITY_SKILLS = [
    {
        "opportunity_id": "opp-solar-rooftop",
        "skill_id": "skill-solar-inst",
        "is_taught": True,
        "priority": 1,
        "skills": {
            "id": "skill-solar-inst",
            "name": "Solar PV Rooftop Installation",
            "sector": "Green Jobs",
            "nsqf_level": 4,
            "qp_code": "SGJ/Q0101",
        },
    }
]


class FakeSupabase:
    def __init__(self):
        self.database = {
            "beneficiaries": [],
            "beneficiary_sessions": [],
            "interview_sessions": [],
            "opportunities": deepcopy(SAMPLE_OPPORTUNITIES),
            "opportunity_skills": deepcopy(SAMPLE_OPPORTUNITY_SKILLS),
            "skills": [
                {
                    "id": "skill-solar-inst",
                    "name": "Solar PV Rooftop Installation",
                    "sector": "Green Jobs",
                    "nsqf_level": 4,
                    "qp_code": "SGJ/Q0101",
                }
            ],
        }

    def table(self, table_name):
        return FakeQuery(self.database, table_name)


@pytest.fixture
def recommendation_client():
    fake = FakeSupabase()
    app.dependency_overrides[get_supabase_client] = lambda: fake
    with TestClient(app) as test_client:
        yield test_client, fake
    app.dependency_overrides.clear()


def seed_beneficiary_with_capability(
    fake,
    state_id="state-up",
    district_id="dist-up-varanasi",
    education="10th_pass",
    mobility="within_15km",
    goal="training_stipend",
):
    ben_id = uuid4()
    fake.database["beneficiaries"].append(
        {
            "id": str(ben_id),
            "name": "Soham Das",
            "preferred_language": "hi",
            "state_id": state_id,
            "district_id": district_id,
            "education_level": education,
            "current_occupation": "solar technician",
            "mobility_preference": mobility,
            "primary_goal": goal,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    token = generate_capability_token()
    fake.database["beneficiary_sessions"].append(
        {
            "id": str(uuid4()),
            "beneficiary_id": str(ben_id),
            "token_hash": hash_capability_token(token),
            "expires_at": "2999-01-01T00:00:00+00:00",
            "revoked_at": None,
            "last_used_at": None,
        }
    )
    return ben_id, token


def seed_completed_interview(fake, beneficiary_id, responses):
    interview_id = uuid4()
    fake.database["interview_sessions"].append(
        {
            "id": str(interview_id),
            "beneficiary_id": str(beneficiary_id),
            "language": "hi",
            "status": "completed",
            "responses": responses,
            "extracted_profile": None,
            "revision": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return interview_id


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# 1. AUTHENTICATION & SECURITY TESTS
# ============================================================================


def test_recommendations_requires_authorization(recommendation_client):
    client, fake = recommendation_client
    ben_id, _ = seed_beneficiary_with_capability(fake)

    res = client.get(f"/api/beneficiaries/{ben_id}/recommendations")
    assert res.status_code == 401
    assert "WWW-Authenticate" in res.headers


def test_recommendations_rejects_invalid_bearer(recommendation_client):
    client, fake = recommendation_client
    ben_id, _ = seed_beneficiary_with_capability(fake)

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert res.status_code == 401


def test_recommendations_rejects_expired_capability(recommendation_client):
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(fake)
    fake.database["beneficiary_sessions"][0]["expires_at"] = "2020-01-01T00:00:00+00:00"

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 401


def test_recommendations_rejects_revoked_capability(recommendation_client):
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(fake)
    fake.database["beneficiary_sessions"][0]["revoked_at"] = datetime.now(timezone.utc).isoformat()

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 401


def test_recommendations_blocks_idor_beneficiary_mismatch(recommendation_client):
    client, fake = recommendation_client
    ben1, token1 = seed_beneficiary_with_capability(fake)
    ben2, _ = seed_beneficiary_with_capability(fake)

    res = client.get(
        f"/api/beneficiaries/{ben2}/recommendations",
        headers=auth_header(token1),
    )
    assert res.status_code == 403


def test_recommendations_rejects_nonexistent_beneficiary(recommendation_client):
    client, fake = recommendation_client
    unknown_ben = uuid4()
    token = generate_capability_token()
    fake.database["beneficiary_sessions"].append(
        {
            "id": str(uuid4()),
            "beneficiary_id": str(unknown_ben),
            "token_hash": hash_capability_token(token),
            "expires_at": "2999-01-01T00:00:00+00:00",
            "revoked_at": None,
            "last_used_at": None,
        }
    )

    res = client.get(
        f"/api/beneficiaries/{unknown_ben}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 404


# ============================================================================
# 2. INCOMPLETE INTERVIEW BEHAVIOR
# ============================================================================


def test_recommendations_returns_clear_message_when_no_interview(recommendation_client):
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(fake)

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["has_completed_interview"] is False
    assert data["recommendations"] == []
    assert "completed before recommendations" in data["message"]


def test_recommendations_returns_draft_id_when_interview_incomplete(recommendation_client):
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(fake)
    draft_id = uuid4()
    fake.database["interview_sessions"].append(
        {
            "id": str(draft_id),
            "beneficiary_id": str(ben_id),
            "language": "hi",
            "status": "draft",
            "responses": {"education": "10th_pass"},
            "revision": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["has_completed_interview"] is False
    assert data["interview_id"] == str(draft_id)
    assert data["recommendations"] == []


# ============================================================================
# 3. PARITY WITH 5 CORE MATCHING TEST CASES
# ============================================================================


def test_case_1_strong_match_scenario(recommendation_client):
    """Case 1: 10th pass, wants solar electrical maintenance, travels up to 15km."""
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(
        fake,
        state_id="state-up",
        district_id="dist-up-varanasi",
    )
    seed_completed_interview(
        fake,
        ben_id,
        {
            "workInterest": "solar and electrical maintenance",
            "education": "10th Pass",
            "mobility": "Up to 15 km (Nearby Market / Town)",
            "preference": "Certified Training + Monthly Stipend",
        },
    )

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["has_completed_interview"] is True
    recs = data["recommendations"]
    assert len(recs) > 0

    top = recs[0]
    assert top["opportunity_id"] == "opp-solar-rooftop"
    assert top["eligible"] is True
    assert top["score"] >= 85
    assert len(top["unmet_criteria"]) == 0
    assert len(top["reasons"]) > 0
    assert len(top["skills"]) > 0
    assert top["skills"][0]["qp_code"] == "SGJ/Q0101"


def test_case_2_geographic_mismatch_scenario(recommendation_client):
    """Case 2: Varanasi scheme vs Kolkata beneficiary."""
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(
        fake,
        state_id="state-wb",
        district_id="dist-wb-kolkata",
    )
    seed_completed_interview(
        fake,
        ben_id,
        {
            "workInterest": "handloom weaving",
            "education": "10th Pass",
            "mobility": "village_block",
            "preference": "micro_business",
        },
    )

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    ineligible = data["ineligible_opportunities"]
    varanasi_match = next((item for item in ineligible if item["opportunity_id"] == "opp-pm-ajay-handloom-varanasi"), None)

    assert varanasi_match is not None
    assert varanasi_match["eligible"] is False
    assert any("state-up" in c for c in varanasi_match["unmet_criteria"])


def test_case_2b_missing_canonical_location(recommendation_client):
    """Case 2B: Missing canonical location rejects restricted opportunity."""
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(
        fake,
        state_id=None,
        district_id=None,
    )
    seed_completed_interview(
        fake,
        ben_id,
        {
            "workInterest": "handloom weaving",
            "education": "10th Pass",
            "mobility": "village_block",
            "preference": "micro_business",
        },
    )

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    ineligible = data["ineligible_opportunities"]
    varanasi_match = next((item for item in ineligible if item["opportunity_id"] == "opp-pm-ajay-handloom-varanasi"), None)

    assert varanasi_match is not None
    assert varanasi_match["eligible"] is False
    assert any("Canonical State and District" in c for c in varanasi_match["unmet_criteria"])


def test_case_3_education_mismatch_scenario(recommendation_client):
    """Case 3: Drone pilot requires 10th pass; beneficiary has no formal schooling."""
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(fake)
    seed_completed_interview(
        fake,
        ben_id,
        {
            "workInterest": "farming and drone spraying",
            "education": "No formal schooling (Eager to learn)",
            "mobility": "district_wide",
            "preference": "job_placement",
        },
    )

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    ineligible = data["ineligible_opportunities"]
    drone_match = next((item for item in ineligible if item["opportunity_id"] == "opp-kisan-drone-pilot"), None)

    assert drone_match is not None
    assert drone_match["eligible"] is False
    assert any("10th pass" in c for c in drone_match["unmet_criteria"])


def test_case_4_mobility_mismatch_scenario(recommendation_client):
    """Case 4: Drone pilot requires district-wide travel; beneficiary village-only."""
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(fake)
    seed_completed_interview(
        fake,
        ben_id,
        {
            "workInterest": "agriculture and drone pilot",
            "education": "10th Pass",
            "mobility": "Within my own village / block",
            "preference": "job_placement",
        },
    )

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    ineligible = data["ineligible_opportunities"]
    drone_match = next((item for item in ineligible if item["opportunity_id"] == "opp-kisan-drone-pilot"), None)

    assert drone_match is not None
    assert drone_match["eligible"] is False
    assert any("district wide" in c for c in drone_match["unmet_criteria"])


def test_case_5_partial_match_scenario(recommendation_client):
    """Case 5: Eligible for Solar, but goal is micro-business instead of training stipend."""
    client, fake = recommendation_client
    ben_id, token = seed_beneficiary_with_capability(fake)
    seed_completed_interview(
        fake,
        ben_id,
        {
            "workInterest": "solar maintenance",
            "education": "12th Pass",
            "mobility": "Up to 15 km",
            "preference": "Start My Own Micro-Business / Shop",
        },
    )

    res = client.get(
        f"/api/beneficiaries/{ben_id}/recommendations",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    recs = data["recommendations"]
    solar_match = next((item for item in recs if item["opportunity_id"] == "opp-solar-rooftop"), None)

    assert solar_match is not None
    assert solar_match["eligible"] is True
    assert 60 <= solar_match["score"] < 95
    assert len(solar_match["reasons"]) > 0


# ============================================================================
# 4. DETERMINISTIC SCORING & TIE-BREAKING TESTS
# ============================================================================


def test_deterministic_tie_breaker_uses_nsqf_and_id():
    """Identical score resolved by NSQF level descending, then opportunity_id ascending."""
    cand = {
        "trade": "general tech",
        "education": "10th_pass",
        "mobility": "within_15km",
        "goal": "training_stipend",
    }
    opp_a = {
        "id": "opp-z-scheme",
        "category": "Technology",
        "nsqf_level": 4,
        "education_min": "10th_pass",
        "mobility_requirement": "within_15km",
        "primary_goal_fit": "training_stipend",
    }
    opp_b = {
        "id": "opp-a-scheme",
        "category": "Technology",
        "nsqf_level": 4,
        "education_min": "10th_pass",
        "mobility_requirement": "within_15km",
        "primary_goal_fit": "training_stipend",
    }

    score_a, _ = calculate_match_score(cand, opp_a)
    score_b, _ = calculate_match_score(cand, opp_b)
    assert score_a == score_b

    # Sorting with key: (-score, -(nsqf_level or 0), opportunity_id)
    items = [opp_a, opp_b]
    items.sort(key=lambda o: (-score_a, -(o.get("nsqf_level") or 0), o["id"]))
    assert items[0]["id"] == "opp-a-scheme"
    assert items[1]["id"] == "opp-z-scheme"


def test_multilingual_normalizers():
    assert normalize_education("10वीं पास") == "10th_pass"
    assert normalize_education("মাধ্যমিক") == "10th_pass"
    assert normalize_education("স্নাতক") == "graduate"
    assert normalize_education("No formal education") == "no_formal"

    assert normalize_mobility("अपने जिले के भीतर") == "district_wide"
    assert normalize_mobility("জেলা জুড়ে") == "district_wide"
    assert normalize_mobility("হোস্টেল") == "relocate_hostel"
    assert normalize_mobility("village block") == "village_block"

    assert normalize_goal("পাক্কা চাকরি") == "job_placement"
    assert normalize_goal("स्वयं की दुकान") == "micro_business"
    assert normalize_goal("stipend training") == "training_stipend"
