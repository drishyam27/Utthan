"""
Tests for Phase 3C: Groq-Powered Structured Profile Extraction & Conversational Clarification.
Validates:
- Multilingual transcript extraction (Hindi, Bengali, English, Hinglish/Banglish)
- Strict schema validation and deterministic normalization
- Ambiguity detection and adaptive clarification questions
- Contradiction detection between previous facts and new statements
- Graceful degradation on API error / timeout / rate limits
- Security and session authorization boundaries
- Zero hallucination guardrails
"""

import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from starlette.testclient import TestClient

from app.core.config import settings
from app.db.supabase import get_supabase_client
from app.main import app
from app.schemas.adaptive_interview import (
    AdaptiveQuestion,
    InterviewStage,
    NSQFCompetencyEvidence,
    StructuredBeneficiaryProfile,
)
from app.schemas.groq_extraction import (
    ExtractedProfileFields,
    InterpretationResult,
)
from app.security.anonymous_session import generate_capability_token, hash_capability_token
from app.services.groq_service import (
    _sanitize_llm_json,
    detect_profile_contradictions,
    deterministic_pre_match,
    interpret_transcript_with_groq,
    validate_and_normalize_extracted_fields,
)
from tests.test_adaptive_interview import FakeSupabase, seed_test_beneficiary


@pytest.fixture
def test_client_fixture():
    fake = FakeSupabase()
    app.dependency_overrides[get_supabase_client] = lambda: fake
    with TestClient(app) as client:
        yield client, fake
    app.dependency_overrides.clear()


# ==============================================================================
# 1. Extraction & Normalization Tests (Hindi, Bengali, English, Mixed)
# ==============================================================================

def test_extract_hindi_transcript_with_groq_mock():
    """Validates extraction of Hindi voice response into structured profile fields."""
    import asyncio
    transcript = "मैंने ITI में electrician किया है और करीब तीन साल से घरों में wiring का काम कर रहा हूं।"
    mock_groq_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "extracted_fields": {
                        "education": None,
                        "vocational_training_has": True,
                        "vocational_training_type": "iti",
                        "experience_years": 3.0,
                        "experience_domain": "electrical wiring",
                        "interested_sector_slug": "electronics-hw",
                        "skills": ["house wiring", "electrician"],
                        "tools_familiarity": ["multimeter", "tester", "screwdriver"],
                        "notional_hours_range": None,
                        "pwd_status": False,
                        "pwd_categories": [],
                    },
                    "confidence": {
                        "vocational_training_type": 0.98,
                        "experience_years": 0.95,
                        "interested_sector_slug": 0.92,
                    },
                    "needs_clarification": False,
                    "clarification_question": None,
                    "reasoning_summary": "Extracted ITI trade and 3 years wiring experience.",
                })
            }
        }]
    }

    dummy_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
    )

    with patch("app.services.groq_service.call_groq_chat_completion", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_groq_response
        result = asyncio.run(interpret_transcript_with_groq(
            transcript=transcript,
            current_stage=InterviewStage.VOCATIONAL_TRAINING,
            current_profile=dummy_profile,
            lang="hi",
        ))

        assert result.needs_clarification is False
        assert result.extracted_fields.vocational_training_type == "iti"
        assert result.extracted_fields.vocational_training_has is True
        assert result.extracted_fields.experience_years == 3.0
        assert result.extracted_fields.interested_sector_slug == "electronics-hw"
        assert "house wiring" in result.extracted_fields.skills


def test_extract_bengali_transcript_with_groq_mock():
    """Validates extraction of Bengali voice transcript."""
    import asyncio
    transcript = "আমি ক্লাস ১০ পাস করেছি এবং ২ বছর ইলেকট্রিক্যাল ওয়্যারিং এর কাজ করেছি।"
    mock_groq_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "extracted_fields": {
                        "education": "10th",
                        "experience_years": 2.0,
                        "experience_domain": "electrical wiring",
                        "interested_sector_slug": "electronics-hw",
                        "skills": ["wiring"],
                        "tools_familiarity": ["tester"],
                    },
                    "confidence": {
                        "education": 0.96,
                        "experience_years": 0.94,
                    },
                    "needs_clarification": False,
                })
            }
        }]
    }

    dummy_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
    )

    with patch("app.services.groq_service.call_groq_chat_completion", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_groq_response
        result = asyncio.run(interpret_transcript_with_groq(
            transcript=transcript,
            current_stage=InterviewStage.EDUCATION,
            current_profile=dummy_profile,
            lang="bn",
        ))

        assert result.extracted_fields.education == "10th"
        assert result.extracted_fields.experience_years == 2.0


def test_extract_english_and_mixed_language_transcript():
    """Validates mixed language transliteration (Banglish/Hinglish)."""
    import asyncio
    transcript = "ami ITI korechi ar 6 month electrical kaj korechi"
    mock_groq_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "extracted_fields": {
                        "vocational_training_has": True,
                        "vocational_training_type": "iti",
                        "experience_years": 0.5,
                        "experience_domain": "electrical",
                    },
                    "confidence": {
                        "vocational_training_type": 0.90,
                        "experience_years": 0.92,
                    },
                    "needs_clarification": False,
                })
            }
        }]
    }

    dummy_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
    )

    with patch("app.services.groq_service.call_groq_chat_completion", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_groq_response
        result = asyncio.run(interpret_transcript_with_groq(
            transcript=transcript,
            current_stage=InterviewStage.EXPERIENCE,
            current_profile=dummy_profile,
            lang="bn",
        ))

        assert result.extracted_fields.vocational_training_type == "iti"
        assert result.extracted_fields.experience_years == 0.5


# ==============================================================================
# 2. Validation & Normalization Layer Tests
# ==============================================================================

def test_validate_and_normalize_canonical_fields():
    """Verifies that ungrounded / unsupported values are rejected or flagged."""
    raw = ExtractedProfileFields(
        education="10th_pass",
        vocational_training_type="2-year NTC",
        experience_years=2.5,
        interested_sector_slug="farming",
        notional_hours_range="401-600",
        pwd_status=True,
        pwd_categories=["LD"],
    )
    active_sectors = ["agriculture", "electronics-hw", "healthcare"]

    normalized, unresolved = validate_and_normalize_extracted_fields(raw, active_sectors)

    assert normalized.education == "10th"
    assert normalized.vocational_training_type == "2_year_ntc"
    assert normalized.experience_years == 2.5
    assert normalized.interested_sector_slug == "agriculture"  # Mapped alias 'farming' -> 'agriculture'
    assert normalized.notional_hours_range == "401–600"
    assert normalized.pwd_status is True
    assert "LD" in normalized.pwd_categories
    assert len(unresolved) == 0


def test_validate_rejects_unsupported_education():
    """Verifies that arbitrary unsupported education category is moved to unresolved."""
    raw = ExtractedProfileFields(
        education="space_astronaut_certification",
    )
    active_sectors = ["agriculture"]

    normalized, unresolved = validate_and_normalize_extracted_fields(raw, active_sectors)
    assert normalized.education is None
    assert "education" in unresolved


# ==============================================================================
# 3. Contradiction Detection Tests
# ==============================================================================

def test_contradiction_detection_for_experience_and_education():
    """Detects conflict between established profile facts and new natural-language claims."""
    current_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        education="8th",
        education_label="8वीं पास",
        work_experience_years=2.0,
        work_experience_label="2 वर्ष",
    )

    new_extracted = ExtractedProfileFields(
        education="graduate",
        experience_years=6.0,
    )

    contradictions, clarify_q = detect_profile_contradictions(
        new_extracted,
        current_profile,
        lang="hi",
    )

    assert len(contradictions) == 2
    fields = [c.field for c in contradictions]
    assert "experience_years" in fields
    assert "education" in fields
    assert clarify_q is not None
    assert "2" in clarify_q and "6" in clarify_q


# ==============================================================================
# 4. Ambiguity & Clarification Generation Tests
# ==============================================================================

def test_ambiguity_triggers_clarification_flag():
    """Verifies that an ambiguous statement yields needs_clarification=True and localized prompt."""
    import asyncio
    transcript = "मुझे थोड़ा बहुत काम आता है पर पता नहीं कौन सा।"
    mock_groq_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "extracted_fields": {
                        "education": None,
                        "experience_years": None,
                    },
                    "confidence": {
                        "experience_years": 0.25,
                    },
                    "needs_clarification": True,
                    "clarification_question": "आप किस तरह का काम सबसे ज्यादा करना पसंद करते हैं?",
                    "reasoning_summary": "Beneficiary expressed uncertainty about specific skills.",
                })
            }
        }]
    }

    dummy_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
    )

    with patch("app.services.groq_service.call_groq_chat_completion", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_groq_response
        result = asyncio.run(interpret_transcript_with_groq(
            transcript=transcript,
            current_stage=InterviewStage.EXPERIENCE,
            current_profile=dummy_profile,
            lang="hi",
        ))

        assert result.needs_clarification is True
        assert result.clarification_question is not None


# ==============================================================================
# 5. Fault Tolerance & Graceful Degradation Tests
# ==============================================================================

def test_graceful_fallback_on_groq_api_failure():
    """Ensures interview degrades gracefully to deterministic fallback on Groq error."""
    import asyncio
    dummy_profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
    )

    # Simulate upstream network failure
    with patch("app.services.groq_service.call_groq_chat_completion", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = RuntimeError("Groq API rate limit exceeded (429)")

        result = asyncio.run(interpret_transcript_with_groq(
            transcript="3 years experience",
            current_stage=InterviewStage.EXPERIENCE,
            current_profile=dummy_profile,
            lang="en",
        ))

        # Must not crash!
        assert result is not None
        assert result.extracted_fields.experience_years == 3.0
        assert "fallback" in result.confidence


def test_sanitize_llm_json_utility():
    """Tests stripping of markdown code fences and think tags."""
    raw = "<think>Analysing user input</think>```json\n{\"needs_clarification\": false}\n```"
    cleaned = _sanitize_llm_json(raw)
    assert cleaned == "{\"needs_clarification\": false}"


# ==============================================================================
# 6. API Route Integration Tests (POST /api/adaptive-interview/{id}/interpret)
# ==============================================================================

def test_api_interpret_endpoint_end_to_end(test_client_fixture):
    """End-to-end integration test of /api/adaptive-interview/{id}/interpret."""
    client, fake = test_client_fixture
    b_id, token = seed_test_beneficiary(fake)

    # 1. Start session
    start_res = client.post(
        "/api/adaptive-interview/sessions",
        json={"beneficiary_id": b_id, "language": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert start_res.status_code == 201
    interview_id = start_res.json()["interview_id"]

    mock_groq_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "extracted_fields": {
                        "education": "10th",
                    },
                    "confidence": {"education": 0.95},
                    "needs_clarification": False,
                    "clarification_question": None,
                })
            }
        }]
    }

    # 2. Call /interpret
    with patch("app.services.groq_service.call_groq_chat_completion", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_groq_response

        interpret_res = client.post(
            f"/api/adaptive-interview/{interview_id}/interpret",
            json={
                "transcript": "मैंने 10वीं तक पढ़ाई की है।",
                "language": "hi",
                "question_id": "edu_highest_level",
                "apply_to_profile": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert interpret_res.status_code == 200
        data = interpret_res.json()
        assert data["interview_id"] == interview_id
        assert data["clarification_needed"] is False
        assert data["updated_state"]["profile_summary"]["education"] == "10th"


def test_api_interpret_endpoint_security_authorization(test_client_fixture):
    """Verifies that unauthorized or mismatched capability tokens are rejected."""
    client, fake = test_client_fixture
    b_id, token = seed_test_beneficiary(fake)

    # Other beneficiary
    other_b_id, other_token = seed_test_beneficiary(fake)

    start_res = client.post(
        "/api/adaptive-interview/sessions",
        json={"beneficiary_id": b_id, "language": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    interview_id = start_res.json()["interview_id"]

    # Attempt to access with other beneficiary's token
    res = client.post(
        f"/api/adaptive-interview/{interview_id}/interpret",
        json={"transcript": "hello", "language": "hi"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403
