"""
Tests for Opportunities Catalog Endpoints.
"""


def test_list_opportunities(client):
    response = client.get("/api/opportunities")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert data["total"] == 2
    assert len(data["opportunities"]) == 2


def test_filter_opportunities_by_category(client):
    response = client.get("/api/opportunities?category=Green")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["opportunities"][0]["id"] == "opp-pm-vishwakarma-solar"


def test_filter_opportunities_by_education(client):
    response = client.get("/api/opportunities?education=10th_pass")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["opportunities"][0]["id"] == "opp-pm-surya-ghar"


def test_filter_opportunities_by_state(client):
    # state-up should include the state-specific scheme AND pan-India scheme
    response = client.get("/api/opportunities?state_id=state-up")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


def test_get_opportunity_detail_valid(client):
    response = client.get("/api/opportunities/opp-pm-vishwakarma-solar")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "opp-pm-vishwakarma-solar"
    assert data["title"] == "PM Vishwakarma - Solar PV Installation & Maintenance"
    assert "skills" in data
    assert len(data["skills"]) == 1
    assert data["skills"][0]["name"] == "Solar PV Rooftop Installation"
    assert data["skills"][0]["nsqf_level"] == 4


def test_get_opportunity_not_found(client):
    response = client.get("/api/opportunities/non-existent-opportunity-xyz")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
