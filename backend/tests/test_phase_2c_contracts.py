"""Focused Phase 2C-1 contract, capability, and migration-assumption tests."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.anonymous_session import AnonymousSessionRecord
from app.schemas.beneficiary import BeneficiaryProfileContract
from app.schemas.interview import InterviewSessionContract
from app.schemas.recommendation import (
    RecommendationResponseContract,
    RecommendationResultContract,
    RecommendationSkillMetadata,
)
from app.security.anonymous_session import (
    generate_capability_token,
    hash_capability_token,
    verify_capability_token,
)


def test_beneficiary_contract_uses_application_categorical_values():
    profile = BeneficiaryProfileContract(
        name="Asha",
        preferred_language="hi",
        state_id="state-up",
        district_id="dist-up-varanasi",
        education_level="10th_pass",
        mobility_preference="district_wide",
        primary_goal="job_placement",
    )

    assert profile.state_id == "state-up"
    assert profile.district_id == "dist-up-varanasi"
    assert profile.education_level == "10th_pass"


@pytest.mark.parametrize(
    "field,value",
    [
        ("preferred_language", "xx"),
        ("education_level", "5th_pass"),
        ("mobility_preference", "national"),
        ("primary_goal", "loan_only"),
    ],
)
def test_beneficiary_contract_rejects_unknown_categorical_values(field, value):
    with pytest.raises(ValidationError):
        BeneficiaryProfileContract(**{field: value})


def test_interview_contract_supports_draft_and_completed_lifecycle():
    draft = InterviewSessionContract(language="en", responses={"education": "10th_pass"})
    assert draft.status == "draft"
    assert draft.revision == 1
    assert draft.completed_at is None

    completed_at = datetime.now(timezone.utc)
    completed = InterviewSessionContract(
        id=uuid4(),
        beneficiary_id=uuid4(),
        language="en",
        status="completed",
        responses={"education": "10th_pass"},
        extracted_profile={"education_level": "10th_pass"},
        revision=2,
        completed_at=completed_at,
    )
    assert completed.status == "completed"
    assert completed.extracted_profile == {"education_level": "10th_pass"}


def test_completed_interview_requires_completion_timestamp():
    with pytest.raises(ValidationError):
        InterviewSessionContract(status="completed")
    with pytest.raises(ValidationError):
        InterviewSessionContract(status="draft", completed_at=datetime.now(timezone.utc))


def test_anonymous_capability_token_is_high_entropy_and_hash_only():
    token = generate_capability_token()
    token_hash = hash_capability_token(token)

    assert len(token) >= 40
    assert len(token_hash) == 64
    assert token not in token_hash
    assert verify_capability_token(token, token_hash)
    assert not verify_capability_token("different-token", token_hash)
    assert not verify_capability_token("", token_hash)
    assert not verify_capability_token(token, "")


def test_anonymous_session_record_contains_no_raw_token():
    token = generate_capability_token()
    token_hash = hash_capability_token(token)
    record = AnonymousSessionRecord(
        id=uuid4(),
        beneficiary_id=uuid4(),
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        created_at=datetime.now(timezone.utc),
    )

    assert token not in repr(record)
    assert record.token_hash == token_hash


def test_recommendation_contract_carries_deterministic_and_nsqf_metadata():
    result = RecommendationResultContract(
        opportunity_id="opp-pm-ajay-handloom-varanasi",
        eligible=True,
        score=92,
        matched_criteria=["Geographic location matches program jurisdiction"],
        reasons=["Direct alignment with selected craft interest"],
        nsqf_level=4,
        qp_code="TSC/Q7301",
        skills=[
            RecommendationSkillMetadata(
                id="skill-loom-jacquard",
                name="Jacquard Loom Operation & Natural Dyeing",
                nsqf_level=4,
                qp_code="TSC/Q7301",
                is_taught=True,
            )
        ],
    )
    response = RecommendationResponseContract(
        beneficiary_id=uuid4(),
        state_id="state-up",
        district_id="dist-up-varanasi",
        generated_at=datetime.now(timezone.utc),
        recommendations=[result],
    )

    assert response.recommendations[0].score == 92
    assert response.recommendations[0].skills[0].qp_code == "TSC/Q7301"


def test_recommendation_contract_rejects_invalid_score_and_nsqf_level():
    with pytest.raises(ValidationError):
        RecommendationResultContract(opportunity_id="opp", eligible=True, score=101)
    with pytest.raises(ValidationError):
        RecommendationSkillMetadata(id="skill", name="Skill", nsqf_level=9)


def test_phase_2c_migration_contains_canonical_foreign_keys_and_private_boundary():
    migration_path = (
        Path(__file__).resolve().parents[2]
        / "supabase"
        / "migrations"
        / "20260915000003_phase_2c_contract_foundation.sql"
    )
    migration = migration_path.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS beneficiary_sessions" in migration
    assert "beneficiary_id UUID NOT NULL REFERENCES beneficiaries(id)" in migration
    assert "DROP POLICY IF EXISTS \"Public select beneficiaries\"" in migration
    assert "REVOKE ALL PRIVILEGES ON TABLE beneficiaries, interview_sessions, beneficiary_sessions, applications" in migration
    assert "states, districts, skills, opportunities, and opportunity_skills" in migration
