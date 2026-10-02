"""
Tests for Utthan Authoritative NSQF / NQR Course Catalog Service and API.
"""

import pytest
from starlette.testclient import TestClient

from app.main import app
from app.services.nsqf_ingestion import (
    slugify,
    normalize_text,
    parse_level,
    parse_hours,
    get_notional_hour_range,
    EXCLUDED_SECTORS,
)
from app.services.nsqf_service import (
    list_sectors,
    query_courses,
    get_course_detail,
    get_catalog_stats,
)

client = TestClient(app)


def test_slugify():
    assert slugify("IT-ITeS") == "it-ites"
    assert slugify("Aerospace & Aviation") == "aerospace-aviation"
    assert slugify("Persons with Disability") == "persons-with-disability"
    assert slugify("Electronics & HW") == "electronics-hw"


def test_normalize_text():
    assert normalize_text("  Automotive   ") == "Automotive"
    assert normalize_text(None) == ""
    # Unicode ligatures
    assert normalize_text("\ufb03ce") == "ffice"


def test_parse_level():
    assert parse_level("4") == 4.0
    assert parse_level("Level 2.5") == 2.5
    assert parse_level("5.5") == 5.5
    assert parse_level(None) is None
    assert parse_level("N/A") is None


def test_parse_hours():
    assert parse_hours("510") == 510
    assert parse_hours("400 hours") == 400
    assert parse_hours("") is None
    assert parse_hours(None) is None


def test_notional_hour_range():
    assert get_notional_hour_range(150) == "1–200"
    assert get_notional_hour_range(300) == "201–400"
    assert get_notional_hour_range(500) == "401–600"
    assert get_notional_hour_range(700) == "601–800"
    assert get_notional_hour_range(900) == "801–1000"
    assert get_notional_hour_range(1100) == "1001–1200"
    assert get_notional_hour_range(1800) == "1201–2400"
    assert get_notional_hour_range(2500) == "Above 2401"
    assert get_notional_hour_range(None) is None


def test_excluded_sectors_list():
    assert "Judiciary" in EXCLUDED_SECTORS
    assert "Indian Defence Forces" in EXCLUDED_SECTORS
    assert "Railways" in EXCLUDED_SECTORS
    assert "Tobacco Industry" in EXCLUDED_SECTORS
    assert len(EXCLUDED_SECTORS) == 15


def test_api_list_sectors():
    res = client.get("/api/nsqf/sectors")
    assert res.status_code == 200
    sectors = res.json()
    assert len(sectors) == 44
    sector_names = [s["name"] for s in sectors]
    assert "IT-ITeS" in sector_names
    assert "Agriculture" in sector_names
    assert "Persons with Disability" in sector_names


def test_api_catalog_stats():
    res = client.get("/api/nsqf/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_courses"] == 2810
    assert stats["total_sectors"] == 44
    assert stats["pwd_courses_count"] >= 231
    assert "4.0" in stats["levels_distribution"]
    assert stats["levels_distribution"]["4.0"] == 843


def test_api_search_courses_pagination():
    res = client.get("/api/nsqf/courses?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2810
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 281


def test_api_filter_by_sector():
    res = client.get("/api/nsqf/courses?sector_id=it-ites&page_size=50")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 316
    for item in data["items"]:
        assert item["sector_id"] == "it-ites"


def test_api_filter_by_level():
    res = client.get("/api/nsqf/courses?nsqf_level=2.5")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 117
    for item in data["items"]:
        assert item["nsqf_level"] == 2.5


def test_api_filter_by_level_range():
    res = client.get("/api/nsqf/courses?min_level=6.0&max_level=7.0")
    assert res.status_code == 200
    data = res.json()
    # Level 6.0: 149, Level 6.5: 8, Level 7.0: 5 -> total = 162
    assert data["total"] == 162
    for item in data["items"]:
        assert 6.0 <= item["nsqf_level"] <= 7.0


def test_api_filter_pwd_courses():
    res = client.get("/api/nsqf/courses?is_pwd=true&page_size=50")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 231
    for item in data["items"]:
        assert item["is_pwd"] is True


def test_api_filter_pwd_category():
    res = client.get("/api/nsqf/courses?pwd_category=VI")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert "VI" in item["pwd_categories"]


def test_api_search_keyword():
    res = client.get("/api/nsqf/courses?search=Electrician")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    # At least one result has electrician in the title
    titles = [item["title"].lower() for item in data["items"]]
    assert any("electrician" in t for t in titles)


def test_api_get_course_by_code():
    res = client.get("/api/nsqf/courses/2022/AA/AASSC/06397")
    assert res.status_code == 200
    course = res.json()
    assert course["q_code"] == "2022/AA/AASSC/06397"
    assert "Airport Terminal Operations Executive" in course["title"]
    assert course["sector_id"] == "aerospace-aviation"
    assert course["nsqf_level"] == 4.0


def test_api_get_nonexistent_course_returns_404():
    res = client.get("/api/nsqf/courses/NON_EXISTENT_COURSE_CODE_12345")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
