"""
Tests for Phase 3B: Adaptive Beneficiary Interview & Structured Beneficiary Profile.
Validates:
- Deterministic 13-stage state machine
- Catalog-aware question generation and NSQF competency evidence collection
- Answer submission, profile normalization, and legacy responses sync
- Field correction during review stage
- PwD disability categories preservation
- Notional hours buckets and education levels
- Final completion and locking
"""

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from starlette.testclient import TestClient

from app.db.supabase import get_supabase_client
from app.main import app
from app.schemas.adaptive_interview import (
    AdaptiveAnswerSubmit,
    InputMethod,
    InterviewStage,
    ProfileFieldCorrectionRequest,
)
from app.security.anonymous_session import generate_capability_token, hash_capability_token


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

    def select(self, _columns="*", count=None):
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
        rows = self.database.setdefault(self.table_name, [])

        if self.mode == "insert":
            row = deepcopy(self.payload)
            row.setdefault("id", str(uuid4()))
            row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            row.setdefault("updated_at", row["created_at"])
            row.setdefault("completed_at", None)
            row.setdefault("extracted_profile", {})
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


class FakeSupabase:
    def __init__(self):
        self.database = {
            "beneficiaries": [],
            "beneficiary_sessions": [],
            "interview_sessions": [],
            "states": [{"id": "delhi", "name": "Delhi"}],
            "districts": [{"id": "central-delhi", "state_id": "delhi", "name": "Central Delhi"}],
            "nsqf_sectors": [
                {"id": "agriculture", "name": "Agriculture", "is_active": True},
                {"id": "green-jobs", "name": "Green Jobs", "is_active": True},
            ],
            "nsqf_qualifications": [
                {
                    "id": "q-1",
                    "q_code": "AGR/Q1201",
                    "title": "Micro Irrigation Technician",
                    "sector_id": "agriculture",
                    "nsqf_level": 4.0,
                    "is_pwd_suitable": True,
                    "total_hours": 400,
                },
                {
                    "id": "q-2",
                    "q_code": "AGR/Q1202",
                    "title": "Drone Pilot / Agri-Tech Operator",
                    "sector_id": "agriculture",
                    "nsqf_level": 4.5,
                    "is_pwd_suitable": False,
                    "total_hours": 500,
                },
            ],
        }

    def table(self, table_name):
        return FakeQuery(self.database, table_name)


@pytest.fixture
def adaptive_client():
    fake = FakeSupabase()
    app.dependency_overrides[get_supabase_client] = lambda: fake
    with TestClient(app) as test_client:
        yield test_client, fake
    app.dependency_overrides.clear()


def seed_test_beneficiary(fake):
    b_id = str(uuid4())
    fake.database["beneficiaries"].append({
        "id": b_id,
        "name": "Ramesh Kumar",
        "preferred_language": "hi",
        "state_id": "delhi",
        "district_id": "central-delhi",
        "education_level": "no_formal",
        "current_occupation": None,
        "mobility_preference": "within_15km",
        "primary_goal": "training_stipend",
    })
    token = generate_capability_token()
    fake.database["beneficiary_sessions"].append({
        "id": str(uuid4()),
        "beneficiary_id": b_id,
        "token_hash": hash_capability_token(token),
        "expires_at": "2999-01-01T00:00:00+00:00",
        "revoked_at": None,
        "last_used_at": None,
    })
    return b_id, token


def test_start_adaptive_session(adaptive_client):
    client, fake = adaptive_client
    b_id, token = seed_test_beneficiary(fake)

    response = client.post(
        "/api/adaptive-interview/sessions",
        json={"beneficiary_id": b_id, "language": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["beneficiary_id"] == b_id
    assert "current_stage" in data
    assert data["current_question"] is not None
    assert data["current_question"]["stage"] in [s.value for s in InterviewStage]
    assert len(data["current_question"]["options"]) > 0


def test_adaptive_stage_progression_and_answer_submission(adaptive_client):
    client, fake = adaptive_client
    b_id, token = seed_test_beneficiary(fake)

    # 1. Start session
    start_res = client.post(
        "/api/adaptive-interview/sessions",
        json={"beneficiary_id": b_id, "language": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert start_res.status_code == 201
    interview_id = start_res.json()["interview_id"]

    # 2. Answer Education (e.g. 10th pass)
    ans1 = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "edu_highest_level",
            "raw_answer": "10वीं पास",
            "normalized_answer": "10th_pass",
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans1.status_code == 200
    state1 = ans1.json()
    assert state1["profile_summary"]["education"] == "10th_pass"
    assert state1["current_stage"] == InterviewStage.VOCATIONAL_TRAINING.value

    # 3. Answer Vocational Training
    ans2 = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "voc_training_type",
            "raw_answer": "आईटीआई (ITI / CTS)",
            "normalized_answer": "iti",
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans2.status_code == 200
    state2 = ans2.json()
    assert state2["profile_summary"]["vocational_training"] is True
    assert state2["profile_summary"]["vocational_training_type"] == "iti"
    assert state2["current_stage"] == InterviewStage.EXPERIENCE.value

    # 4. Answer Work Experience
    ans3 = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "exp_years",
            "raw_answer": "1 से 2 वर्ष",
            "normalized_answer": 2.0,
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans3.status_code == 200
    state3 = ans3.json()
    assert state3["profile_summary"]["work_experience_years"] == 2.0
    assert state3["current_stage"] == InterviewStage.SECTOR.value

    # 5. Answer Sector (Agriculture)
    ans4 = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "sec_interested_sector",
            "raw_answer": "🌾 कृषि एवं बागवानी (Agriculture)",
            "normalized_answer": "agriculture",
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans4.status_code == 200
    state4 = ans4.json()
    assert state4["profile_summary"]["interested_sector_id"] == "agriculture"
    # Stage should now be catalog_context
    assert state4["current_stage"] == InterviewStage.CATALOG_CONTEXT.value
    # Current question should feature catalog qualifications
    assert state4["current_question"]["catalog_context"] is not None



def test_competency_evidence_and_pwd_collection(adaptive_client):
    client, fake = adaptive_client
    b_id, token = seed_test_beneficiary(fake)

    start_res = client.post(
        "/api/adaptive-interview/sessions",
        json={"beneficiary_id": b_id, "language": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    interview_id = start_res.json()["interview_id"]

    # Directly set profile up to CATALOG_CONTEXT
    fake.database["interview_sessions"][0]["extracted_profile"] = {
        "education": "10th_pass",
        "vocational_training": True,
        "vocational_training_type": "iti",
        "work_experience_years": 2.0,
        "interested_sector_id": "agriculture",
        "interested_sector_name": "Agriculture",
    }

    # Submit Catalog Qualification selection
    ans_cat = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "cat_target_qualifications",
            "raw_answer": "Micro Irrigation Technician",
            "normalized_answer": ["AGR/Q1201"],
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans_cat.status_code == 200
    state_cat = ans_cat.json()
    assert "AGR/Q1201" in state_cat["profile_summary"]["target_qualifications"]
    assert state_cat["current_stage"] == InterviewStage.COMPETENCY_EVIDENCE.value

    # Submit Practical Equipment / Competency Evidence
    ans_comp = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "comp_tools_familiarity",
            "raw_answer": "Drip irrigation pipes & sprayers",
            "normalized_answer": ["Drip Irrigation Pipes & Valves", "Power Sprayers"],
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans_comp.status_code == 200
    state_comp = ans_comp.json()
    evidence = state_comp["profile_summary"]["competency_evidence"]
    assert len(evidence["technical_skills"]) > 0
    assert state_comp["current_stage"] == InterviewStage.CAPACITY_HOURS.value

    # Submit Capacity Hours
    ans_hrs = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "cap_notional_hours",
            "raw_answer": "401–600 घंटे",
            "normalized_answer": "401–600",
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans_hrs.status_code == 200
    assert ans_hrs.json()["current_stage"] == InterviewStage.PWD.value

    # Submit PwD Inclusion
    ans_pwd = client.post(
        f"/api/adaptive-interview/{interview_id}/answer",
        json={
            "question_id": "pwd_status_category",
            "raw_answer": "हां (लोकोमोटर दिव्यांगता - LD)",
            "normalized_answer": "pwd_ld",
            "input_method": "option",
            "language": "hi",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ans_pwd.status_code == 200
    state_pwd = ans_pwd.json()
    assert state_pwd["profile_summary"]["pwd_status"] is True
    assert "LD" in state_pwd["profile_summary"]["pwd_categories"]


def test_profile_field_correction_during_review(adaptive_client):
    client, fake = adaptive_client
    b_id, token = seed_test_beneficiary(fake)

    start_res = client.post(
        "/api/adaptive-interview/sessions",
        json={"beneficiary_id": b_id, "language": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    interview_id = start_res.json()["interview_id"]

    # Patch a field (e.g. correct education level)
    patch_res = client.patch(
        f"/api/adaptive-interview/{interview_id}/profile",
        json={"field_name": "education", "value": "12th_pass"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_res.status_code == 200
    patched = patch_res.json()
    assert patched["education"] == "12th_pass"

    # Verify via GET profile
    get_res = client.get(
        f"/api/adaptive-interview/{interview_id}/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["education"] == "12th_pass"


def test_complete_adaptive_interview_locks_and_syncs(adaptive_client):
    client, fake = adaptive_client
    b_id, token = seed_test_beneficiary(fake)

    start_res = client.post(
        "/api/adaptive-interview/sessions",
        json={"beneficiary_id": b_id, "language": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    interview_id = start_res.json()["interview_id"]

    # Pre-populate complete profile
    fake.database["interview_sessions"][0]["extracted_profile"] = {
        "education": "12th_pass",
        "vocational_training": True,
        "vocational_training_type": "iti",
        "work_experience_years": 2.0,
        "interested_sector_id": "agriculture",
        "interested_sector_name": "Agriculture",
        "notional_hours_range": "401–600",
        "pwd_status": False,
        "mobility_preference": "within_15km",
        "primary_goal": "training_stipend",
    }

    # Complete interview
    comp_res = client.post(
        f"/api/adaptive-interview/{interview_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert comp_res.status_code == 200
    final_state = comp_res.json()
    assert final_state["is_completed"] is True
    assert final_state["current_stage"] == InterviewStage.COMPLETED.value

    # Verify session row in database
    session_row = fake.database["interview_sessions"][0]
    assert session_row["status"] == "completed"
    assert session_row["completed_at"] is not None
    # Backward compatible responses must be present
    assert "workInterest" in session_row["responses"]
    assert "education" in session_row["responses"]
    assert "mobility" in session_row["responses"]
    assert "preference" in session_row["responses"]
