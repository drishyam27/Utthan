"""
Test Fixtures & Mock Supabase Client for Utthan Backend Tests.
Allows 100% reproducible testing without requiring production secrets.
"""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.db.supabase import get_supabase_client


class MockPostgrestResponse:
    def __init__(self, data):
        self.data = data


class MockTableQuery:
    def __init__(self, table_name, data):
        self.table_name = table_name
        self._data = data

    def select(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, limit_num):
        return MockTableQuery(self.table_name, self._data[:limit_num])

    def eq(self, column, value):
        filtered = [row for row in self._data if row.get(column) == value]
        return MockTableQuery(self.table_name, filtered)

    def ilike(self, column, pattern):
        pattern_clean = pattern.replace("%", "").lower()
        filtered = [row for row in self._data if pattern_clean in str(row.get(column, "")).lower()]
        return MockTableQuery(self.table_name, filtered)

    def in_(self, column, values):
        filtered = [row for row in self._data if row.get(column) in values]
        return MockTableQuery(self.table_name, filtered)

    def execute(self):
        return MockPostgrestResponse(self._data)


class MockSupabaseClient:
    """In-memory mock for Supabase PostgREST client."""
    def __init__(self):
        self.states = [
            {"id": "state-up", "code": "UP", "name": "Uttar Pradesh", "type": "state", "lgd_code": 9},
            {"id": "state-wb", "code": "WB", "name": "West Bengal", "type": "state", "lgd_code": 19},
            {"id": "ut-dl", "code": "DL", "name": "Delhi (NCT)", "type": "union_territory", "lgd_code": 7}
        ]
        self.districts = [
            {"id": "dist-up-varanasi", "state_id": "state-up", "name": "Varanasi", "code": "UP-VAR", "lgd_district_code": 178},
            {"id": "dist-up-lucknow", "state_id": "state-up", "name": "Lucknow", "code": "UP-LKO", "lgd_district_code": 167},
            {"id": "dist-wb-kolkata", "state_id": "state-wb", "name": "Kolkata", "code": "WB-KOL", "lgd_district_code": 318},
            {"id": "dist-dl-central", "state_id": "ut-dl", "name": "Central", "code": "DL-CD", "lgd_district_code": 77}
        ]
        self.opportunities = [
            {
                "id": "opp-pm-vishwakarma-solar",
                "title": "PM Vishwakarma - Solar PV Installation & Maintenance",
                "category": "Green Energy & Technology",
                "provider": "Ministry of MSME",
                "source": "PM Vishwakarma Official Portal",
                "source_url": "https://pmvishwakarma.gov.in",
                "state_id": "state-up",
                "district_id": "dist-up-varanasi",
                "education_min": "no_formal",
                "age_min": 18,
                "age_max": None,
                "mobility_requirement": "within_15km",
                "stipend": "Rs 500/day during 5-day basic training",
                "expected_earnings": "Rs 15,000 - 25,000/month after certification",
                "duration": "5 days basic + 15 days advanced"
            },
            {
                "id": "opp-pm-surya-ghar",
                "title": "PM Surya Ghar: Muft Bijli Yojana - Rooftop Solar Technician",
                "category": "Renewable Energy & Skilling",
                "provider": "Ministry of New and Renewable Energy (MNRE)",
                "source": "PM Surya Ghar National Portal",
                "source_url": "https://pmsuryaghar.gov.in",
                "state_id": None,
                "district_id": None,
                "education_min": "10th_pass",
                "age_min": 18,
                "age_max": 35,
                "mobility_requirement": "district_wide",
                "stipend": "Free Government Training + Skill India Certification",
                "expected_earnings": "Rs 18,000 - 30,000/month",
                "duration": "3 months (300 hours)"
            }
        ]
        self.skills = [
            {
                "id": "skill-solar-inst",
                "name": "Solar PV Rooftop Installation",
                "sector": "Green Jobs & Renewable Energy",
                "nsqf_level": 4,
                "qp_code": "SGJ/Q0101"
            }
        ]
        self.opportunity_skills = [
            {
                "opportunity_id": "opp-pm-vishwakarma-solar",
                "skill_id": "skill-solar-inst",
                "is_primary": True
            }
        ]

    def table(self, table_name):
        if table_name == "states":
            return MockTableQuery("states", self.states)
        elif table_name == "districts":
            return MockTableQuery("districts", self.districts)
        elif table_name == "opportunities":
            return MockTableQuery("opportunities", self.opportunities)
        elif table_name == "skills":
            return MockTableQuery("skills", self.skills)
        elif table_name == "opportunity_skills":
            return MockTableQuery("opportunity_skills", self.opportunity_skills)
        return MockTableQuery(table_name, [])


@pytest.fixture
def mock_supabase():
    return MockSupabaseClient()


@pytest.fixture
def client(mock_supabase):
    """TestClient with overridden Supabase dependency."""
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
