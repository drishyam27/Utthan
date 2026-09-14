"""
Tests for Health & Root Endpoints.
"""

from unittest.mock import patch


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Utthan API"
    assert data["status"] == "active"
    assert "/docs" in data["docs"]


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Utthan API"
    assert data["version"] == "1.0.0"


def test_openapi_docs_endpoint(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/health" in schema["paths"]
    assert "/api/locations/states" in schema["paths"]
    assert "/api/opportunities" in schema["paths"]


def test_db_health_connected(client):
    with patch("app.api.routes.health.check_db_connection", return_value=(True, "Database connection active and responsive")):
        response = client.get("/api/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"


def test_db_health_disconnected(client):
    with patch("app.api.routes.health.check_db_connection", return_value=(False, "Database connection failed or remote host unreachable")):
        response = client.get("/api/health/db")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert data["database"] == "disconnected"
