"""Focused tests for the Phase 2C-3 persistent interview lifecycle."""

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from starlette.testclient import TestClient

from app.db.supabase import get_supabase_client
from app.main import app
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
        rows = self.database[self.table_name]

        if self.mode == "insert":
            row = deepcopy(self.payload)
            row.setdefault("id", str(uuid4()))
            row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            row.setdefault("updated_at", row["created_at"])
            row.setdefault("completed_at", None)
            row.setdefault("extracted_profile", None)
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
            "beneficiary_sessions": [],
            "interview_sessions": [],
        }

    def table(self, table_name):
        return FakeQuery(self.database, table_name)


@pytest.fixture
def interview_client():
    fake = FakeSupabase()
    app.dependency_overrides[get_supabase_client] = lambda: fake
    with TestClient(app) as test_client:
        yield test_client, fake
    app.dependency_overrides.clear()


def seed_capability(fake, beneficiary_id=None):
    beneficiary_id = beneficiary_id or uuid4()
    token = generate_capability_token()
    fake.database["beneficiary_sessions"].append(
        {
            "id": str(uuid4()),
            "beneficiary_id": str(beneficiary_id),
            "token_hash": hash_capability_token(token),
            "expires_at": "2999-01-01T00:00:00+00:00",
            "revoked_at": None,
            "last_used_at": None,
        }
    )
    return beneficiary_id, token


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_interview(client, beneficiary_id, token):
    response = client.post(
        f"/api/beneficiaries/{beneficiary_id}/interviews",
        headers=headers(token),
        json={"language": "en"},
    )
    assert response.status_code == 201
    return response.json()


VALID_RESPONSES = {
    "workInterest": "☀️ Solar & Electrical Maintenance",
    "education": "🎓 10th Pass",
    "mobility": "🏡 Within my own village / block",
    "preference": "📜 Certified Training + Monthly Stipend",
}


def test_create_is_authorized_draft_and_resume_is_idempotent(interview_client):
    client, fake = interview_client
    beneficiary_id, token = seed_capability(fake)

    first = create_interview(client, beneficiary_id, token)
    second = create_interview(client, beneficiary_id, token)

    assert first["status"] == "draft"
    assert first["revision"] == 1
    assert first["responses"] == {}
    assert first["completed_at"] is None
    assert first["extracted_profile"] is None
    assert second["id"] == first["id"]
    assert len(fake.database["interview_sessions"]) == 1


def test_create_rejects_missing_and_wrong_capability(interview_client):
    client, fake = interview_client
    beneficiary_id, token = seed_capability(fake)
    other_id, other_token = seed_capability(fake)

    assert client.post(f"/api/beneficiaries/{beneficiary_id}/interviews").status_code == 401
    assert client.post(
        f"/api/beneficiaries/{beneficiary_id}/interviews",
        headers=headers(other_token),
        json={"language": "en"},
    ).status_code == 403
    assert other_id != beneficiary_id
    assert token


def test_get_and_idor_are_capability_owned(interview_client):
    client, fake = interview_client
    beneficiary_a, token_a = seed_capability(fake)
    beneficiary_b, token_b = seed_capability(fake)
    interview_a = create_interview(client, beneficiary_a, token_a)
    interview_b = create_interview(client, beneficiary_b, token_b)

    own = client.get(f"/api/interviews/{interview_a['id']}", headers=headers(token_a))
    wrong = client.get(f"/api/interviews/{interview_b['id']}", headers=headers(token_a))
    missing = client.get(f"/api/interviews/{uuid4()}", headers=headers(token_a))

    assert own.status_code == 200
    assert wrong.status_code == 404
    assert missing.status_code == 404
    assert token_a not in wrong.text

    reverse = client.get(f"/api/interviews/{interview_a['id']}", headers=headers(token_b))
    assert reverse.status_code == 404


def test_patch_validates_answers_and_revision(interview_client):
    client, fake = interview_client
    beneficiary_id, token = seed_capability(fake)
    interview = create_interview(client, beneficiary_id, token)
    path = f"/api/interviews/{interview['id']}"

    partial = client.patch(
        path,
        headers=headers(token),
        json={
            "responses": {
                "workInterest": VALID_RESPONSES["workInterest"],
                "education": VALID_RESPONSES["education"],
            },
            "expected_revision": 1,
        },
    )
    stale = client.patch(
        path,
        headers=headers(token),
        json={"responses": VALID_RESPONSES, "expected_revision": 1},
    )
    invalid = client.patch(
        path,
        headers=headers(token),
        json={
            "responses": {"workInterest": "arbitrary transcript"},
            "expected_revision": 2,
        },
    )
    protected = client.patch(
        path,
        headers=headers(token),
        json={"responses": VALID_RESPONSES, "expected_revision": 2, "status": "completed"},
    )

    assert partial.status_code == 200
    assert partial.json()["revision"] == 2
    assert stale.status_code == 409
    assert invalid.status_code == 422
    assert protected.status_code == 422
    assert fake.database["interview_sessions"][0]["status"] == "draft"


def test_completion_requires_all_answers_and_is_final(interview_client):
    client, fake = interview_client
    beneficiary_id, token = seed_capability(fake)
    interview = create_interview(client, beneficiary_id, token)
    path = f"/api/interviews/{interview['id']}"

    incomplete = client.post(
        f"{path}/complete",
        headers=headers(token),
        json={"expected_revision": 1},
    )
    saved = client.patch(
        path,
        headers=headers(token),
        json={"responses": VALID_RESPONSES, "expected_revision": 1},
    )
    complete = client.post(
        f"{path}/complete",
        headers=headers(token),
        json={"expected_revision": saved.json()["revision"]},
    )
    edit_completed = client.patch(
        path,
        headers=headers(token),
        json={"responses": VALID_RESPONSES, "expected_revision": complete.json()["revision"]},
    )
    complete_again = client.post(
        f"{path}/complete",
        headers=headers(token),
        json={"expected_revision": complete.json()["revision"]},
    )

    assert incomplete.status_code == 422
    assert saved.status_code == 200
    assert complete.status_code == 200
    assert complete.json()["status"] == "completed"
    assert complete.json()["completed_at"] is not None
    assert complete.json()["revision"] == 3
    assert edit_completed.status_code == 409
    assert complete_again.status_code == 409
    assert fake.database["interview_sessions"][0]["status"] == "completed"


def test_completed_session_is_returned_by_resume_without_reopening(interview_client):
    client, fake = interview_client
    beneficiary_id, token = seed_capability(fake)
    interview = create_interview(client, beneficiary_id, token)
    path = f"/api/interviews/{interview['id']}"

    saved = client.patch(
        path,
        headers=headers(token),
        json={"responses": VALID_RESPONSES, "expected_revision": 1},
    )
    completed = client.post(
        f"{path}/complete",
        headers=headers(token),
        json={"expected_revision": saved.json()["revision"]},
    )
    resumed = create_interview(client, beneficiary_id, token)

    assert completed.status_code == 200
    assert resumed["id"] == interview["id"]
    assert resumed["status"] == "completed"
    assert len(fake.database["interview_sessions"]) == 1
