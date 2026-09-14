"""
Tests for Location Master Endpoints (States & Districts).
"""


def test_list_states(client):
    response = client.get("/api/locations/states")
    assert response.status_code == 200
    states = response.json()
    assert isinstance(states, list)
    assert len(states) >= 3
    
    # Check structure
    up_state = next((s for s in states if s["code"] == "UP"), None)
    assert up_state is not None
    assert up_state["name"] == "Uttar Pradesh"
    assert up_state["type"] == "state"
    assert up_state["lgd_code"] == 9


def test_list_districts_by_state_code(client):
    # Lookup by short code 'UP'
    response = client.get("/api/locations/states/UP/districts")
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert data["state"]["code"] == "UP"
    assert data["total_districts"] == 2
    assert len(data["districts"]) == 2
    
    district_names = [d["name"] for d in data["districts"]]
    assert "Varanasi" in district_names
    assert "Lucknow" in district_names


def test_list_districts_by_state_id(client):
    # Lookup by state ID 'state-wb'
    response = client.get("/api/locations/states/state-wb/districts")
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["code"] == "WB"
    assert data["total_districts"] == 1
    assert data["districts"][0]["name"] == "Kolkata"


def test_list_districts_invalid_state(client):
    response = client.get("/api/locations/states/NONEXISTENT/districts")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
