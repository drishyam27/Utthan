"""Focused tests for anonymous beneficiary creation, access, and updates."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from starlette.testclient import TestClient

from app.db.supabase import get_supabase_client
from app.main import app
from app.security.anonymous_session import hash_capability_token


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.filters = []
        self.selected = None
        self.limit_value = None
        self.mode = "select"
        self.payload = None

    def select(self, columns):
        self.selected = columns
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def insert(self, payload):
        self.mode = "insert"
        self.payload = deepcopy(payload)
        return self

    def update(self, payload):
        self.mode = "update"
        self.payload = deepcopy(payload)
        return self

    def delete(self):
        self.mode = "delete"
        return self

    def _matches(self, row):
        return all(row.get(column) == value for column, value in self.filters)

    def _project(self, row):
        return deepcopy(row)

    def execute(self):
        rows = self.database[self.table_name]

        if self.mode == "insert":
            row = deepcopy(self.payload)
            if self.table_name == "beneficiaries":
                now = datetime.now(timezone.utc).isoformat()
                row.setdefault("id", str(uuid4()))
                row.setdefault("education_level", "no_formal")
                row.setdefault("mobility_preference", "within_15km")
                row.setdefault("primary_goal", "training_stipend")
                row.setdefault("created_at", now)
                row.setdefault("updated_at", now)
            elif self.table_name == "beneficiary_sessions":
                row.setdefault("id", str(uuid4()))
                row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
                row.setdefault("last_used_at", None)
                row.setdefault("rotated_at", None)
                row.setdefault("revoked_at", None)
            rows.append(row)
            return FakeResponse([self._project(row)])

        matching = [row for row in rows if self._matches(row)]
        if self.limit_value is not None:
            matching = matching[: self.limit_value]

        if self.mode == "update":
            for row in matching:
                row.update(deepcopy(self.payload))
            return FakeResponse([self._project(row) for row in matching])

        if self.mode == "delete":
            self.database[self.table_name] = [row for row in rows if not self._matches(row)]
            return FakeResponse([])

        return FakeResponse([self._project(row) for row in matching])


class FakeSupabase:
    def __init__(self):
        self.database = {
            "states": [
                {"id": "state-up"},
                {"id": "state-wb"},
            ],
            "districts": [
                {"id": "dist-up-varanasi", "state_id": "state-up"},
                {"id": "dist-wb-kolkata", "state_id": "state-wb"},
            ],
            "beneficiaries": [],
            "beneficiary_sessions": [],
        }

    def table(self, table_name):
        return FakeQuery(self.database, table_name)


@pytest.fixture
def beneficiary_client():
    fake = FakeSupabase()
    app.dependency_overrides[get_supabase_client] = lambda: fake
    with TestClient(app) as test_client:
        yield test_client, fake
    app.dependency_overrides.clear()


def create_profile(client, **overrides):
    payload = {
        "name": "Asha Devi",
        "preferred_language": "hi",
        "state_id": "state-up",
        "district_id": "dist-up-varanasi",
    }
    payload.update(overrides)
    response = client.post("/api/beneficiaries", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_returns_capability_once_and_persists_only_hash(beneficiary_client):
    client, fake = beneficiary_client
    result = create_profile(client)

    token = result["session_token"]
    assert len(token) >= 40
    assert "session_token" not in result["beneficiary"]
    assert "token_hash" not in result["beneficiary"]
    assert len(fake.database["beneficiary_sessions"]) == 1
    session = fake.database["beneficiary_sessions"][0]
    assert session["beneficiary_id"] == result["beneficiary"]["id"]
    assert session["token_hash"] == hash_capability_token(token)
    assert token not in session["token_hash"]


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "preferred_language": "hi", "state_id": "state-up", "district_id": "dist-up-varanasi"},
        {"name": "Asha", "preferred_language": "xx", "state_id": "state-up", "district_id": "dist-up-varanasi"},
    ],
)
def test_create_rejects_invalid_payload(beneficiary_client, payload):
    client, _ = beneficiary_client
    response = client.post("/api/beneficiaries", json=payload)
    assert response.status_code == 422


def test_create_rejects_invalid_location_and_mismatch(beneficiary_client):
    client, fake = beneficiary_client

    invalid_state = client.post(
        "/api/beneficiaries",
        json={"name": "Asha", "preferred_language": "hi", "state_id": "state-nope", "district_id": "dist-up-varanasi"},
    )
    mismatch = client.post(
        "/api/beneficiaries",
        json={"name": "Asha", "preferred_language": "hi", "state_id": "state-up", "district_id": "dist-wb-kolkata"},
    )

    assert invalid_state.status_code == 422
    assert mismatch.status_code == 422
    assert fake.database["beneficiaries"] == []


def test_get_requires_matching_valid_capability(beneficiary_client):
    client, _ = beneficiary_client
    first = create_profile(client)
    second = create_profile(client, name="Bina Devi")
    first_headers = {"Authorization": f"Bearer {first['session_token']}"}

    authorized = client.get(f"/api/beneficiaries/{first['beneficiary']['id']}", headers=first_headers)
    mismatch = client.get(f"/api/beneficiaries/{second['beneficiary']['id']}", headers=first_headers)
    missing = client.get(f"/api/beneficiaries/{first['beneficiary']['id']}")
    invalid = client.get(
        f"/api/beneficiaries/{first['beneficiary']['id']}",
        headers={"Authorization": "Bearer invalid-token"},
    )
    nonexistent = client.get(f"/api/beneficiaries/{uuid4()}", headers=first_headers)

    assert authorized.status_code == 200
    assert authorized.json()["name"] == "Asha Devi"
    assert mismatch.status_code == 403
    assert "beneficiary" in mismatch.text.lower()
    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert nonexistent.status_code == 403
    assert first["session_token"] not in mismatch.text
    assert "token_hash" not in authorized.text


def test_expired_and_revoked_capabilities_are_rejected(beneficiary_client):
    client, fake = beneficiary_client
    result = create_profile(client)
    headers = {"Authorization": f"Bearer {result['session_token']}"}
    session = fake.database["beneficiary_sessions"][0]

    session["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    expired = client.get(f"/api/beneficiaries/{result['beneficiary']['id']}", headers=headers)
    assert expired.status_code == 401

    session["expires_at"] = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    session["revoked_at"] = datetime.now(timezone.utc).isoformat()
    revoked = client.get(f"/api/beneficiaries/{result['beneficiary']['id']}", headers=headers)
    assert revoked.status_code == 401


def test_patch_allows_authorized_fields_and_updates_timestamp(beneficiary_client):
    client, fake = beneficiary_client
    result = create_profile(client)
    headers = {"Authorization": f"Bearer {result['session_token']}"}

    response = client.patch(
        f"/api/beneficiaries/{result['beneficiary']['id']}",
        headers=headers,
        json={"name": "Asha Singh", "current_occupation": "Tailor"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Asha Singh"
    assert response.json()["current_occupation"] == "Tailor"
    assert fake.database["beneficiaries"][0]["updated_at"]


def test_patch_rejects_invalid_location_and_protected_fields(beneficiary_client):
    client, _ = beneficiary_client
    result = create_profile(client)
    headers = {"Authorization": f"Bearer {result['session_token']}"}
    base = f"/api/beneficiaries/{result['beneficiary']['id']}"

    invalid_location = client.patch(
        base,
        headers=headers,
        json={"state_id": "state-up", "district_id": "dist-wb-kolkata"},
    )
    protected = client.patch(base, headers=headers, json={"id": str(uuid4())})

    assert invalid_location.status_code == 422
    assert protected.status_code == 422


def test_patch_rejects_capability_for_another_beneficiary(beneficiary_client):
    client, _ = beneficiary_client
    first = create_profile(client)
    second = create_profile(client, name="Bina Devi")
    headers = {"Authorization": f"Bearer {first['session_token']}"}

    response = client.patch(
        f"/api/beneficiaries/{second['beneficiary']['id']}",
        headers=headers,
        json={"name": "Attempted Takeover"},
    )

    assert response.status_code == 403
    assert "Attempted Takeover" not in response.text
