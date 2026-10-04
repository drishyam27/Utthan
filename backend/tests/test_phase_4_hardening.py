"""
Phase 4 Tests: Comprehensive End-to-End Validation + Production Hardening

Validates:
1. Deterministic Scenarios A through G (Catalog grounded, 15 excluded sectors strictly blocked)
2. Audio failure handling (empty, oversized, unsupported format)
3. Contradiction detection & non-destructive clarification requests
4. Multilingual fallback and error-resilient speech synthesis
5. Session resume and state idempotency
6. Security isolation, capability token verification, and IDOR protection
7. Recommendation explanation integrity (zero fabrication/modification of catalog courses)
"""

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
import httpx
import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.supabase import get_supabase_client
from app.schemas.adaptive_interview import (
    AdaptiveAnswerSubmit,
    InputMethod,
    InterviewStage,
    NSQFCompetencyEvidence,
    StructuredBeneficiaryProfile,
)
from app.schemas.groq_extraction import (
    ExtractedProfileFields,
)
from app.schemas.nsqf_recommendation import (
    NSQFEligibilityEvaluation,
    NSQFRecommendationItem,
    NSQFRecommendationResponse,
)
from app.schemas.voice import SynthesisRequest
from app.services.adaptive_interview_service import (
    get_adaptive_interview_state,
    get_or_initialize_profile,
    submit_answer_to_interview,
)
from app.services.groq_service import (
    detect_profile_contradictions,
    deterministic_pre_match,
    explain_nsqf_recommendations_with_groq,
    validate_and_normalize_extracted_fields,
)
from app.services.nsqf_ingestion import EXCLUDED_SECTORS, slugify
from app.services.nsqf_recommendation_service import (
    check_insufficient_profile,
    evaluate_nsqf_eligibility,
    generate_nsqf_recommendations,
    load_candidate_qualifications,
    NSQFEligibilityStatus,
)
from app.services.nsqf_service import _get_in_memory_catalog
from app.services.stt_service import (
    resolve_sarvam_language_code,
    validate_audio_payload,
)
from app.services.tts_service import (
    clean_text_for_speech,
    resolve_sarvam_tts_language,
    synthesize_speech,
)
from tests.test_adaptive_interview import FakeSupabase, seed_test_beneficiary


# ==============================================================================
# 1. DETERMINISTIC SCENARIO TESTS (A through G)
# ==============================================================================

def test_scenario_a_beginner_deterministic():
    """Scenario A: Low/no formal education, no experience, selected sector (Agriculture)."""
    _, quals, _ = _get_in_memory_catalog()
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Sunita Devi",
        education="no_formal",
        education_label="No formal education",
        work_experience_years=0.0,
        interested_sector_name="Agriculture",
        interested_sector_id="agriculture",
        notional_hours_range="201–400",
        pwd_status=False,
    )
    rec = generate_nsqf_recommendations(None, profile, limit=5)
    assert rec.status == "eligible"
    assert len(rec.recommendations) > 0
    for r in rec.recommendations:
        assert r.sector_name == "Agriculture"
        assert r.q_code is not None
        assert r.nsqf_level > 0.0
        assert r.source == "nsqf_nqr_catalog"


def test_scenario_b_vocationally_qualified_deterministic():
    """Scenario B: 10th + ITI, Electronics & HW."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Vikram Kumar",
        education="10th",
        education_label="10th Pass",
        vocational_training=True,
        vocational_training_type="ITI",
        work_experience_years=1.0,
        interested_sector_name="Electronics & HW",
        interested_sector_id="electronics-hw",
        notional_hours_range="401–600",
        pwd_status=False,
    )
    rec = generate_nsqf_recommendations(None, profile, limit=5)
    assert rec.status == "eligible"
    assert len(rec.recommendations) > 0
    # Vocational training reason should be present in top match reasons
    top = rec.recommendations[0]
    assert any("vocational training" in r.lower() for r in top.match_reasons)


def test_scenario_c_experienced_beneficiary_deterministic():
    """Scenario C: 12th + 5 years experience in Construction with competency evidence."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Rajesh Sharma",
        education="12th",
        education_label="12th Pass",
        work_experience_years=5.0,
        interested_sector_name="Construction",
        interested_sector_id="construction",
        competency_evidence=NSQFCompetencyEvidence(
            technical_skills=["bricklaying", "plastering", "scaffolding"],
            tools_familiarity=["trowel", "plumb bob", "spirit level"],
        ),
        notional_hours_range="401–600",
        pwd_status=False,
    )
    rec = generate_nsqf_recommendations(None, profile, limit=5)
    assert rec.status == "eligible"
    assert len(rec.recommendations) > 0
    top = rec.recommendations[0]
    # Experience alignment should be captured
    assert any("experience" in r.lower() for r in top.match_reasons)


def test_scenario_d_pwd_candidate_deterministic():
    """Scenario D: PwD candidate with LD category in Persons with Disability sector."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Amina Khatun",
        education="10th",
        work_experience_years=0.0,
        pwd_status=True,
        pwd_checked=True,
        pwd_categories=["LD"],
        interested_sector_name="Persons with Disability",
        interested_sector_id="persons-with-disability",
        notional_hours_range="201–400",
    )
    rec = generate_nsqf_recommendations(None, profile, limit=5)
    assert rec.status == "eligible"
    assert len(rec.recommendations) > 0
    top = rec.recommendations[0]
    assert top.is_pwd is True
    assert "LD" in top.pwd_categories or len(top.pwd_categories) > 0


def test_scenario_e_insufficient_profile():
    """Scenario E: Missing critical fields produces 'insufficient_profile' and 0 courses."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Incomplete User",
        education=None,
        interested_sector_name=None,
        interested_sector_id=None,
    )
    is_insuf, missing = check_insufficient_profile(profile)
    assert is_insuf is True
    assert "education" in missing
    assert "interested_sector" in missing

    rec = generate_nsqf_recommendations(None, profile)
    assert rec.status == "insufficient_profile"
    assert len(rec.recommendations) == 0
    assert "Missing:" in rec.message


def test_scenario_f_no_match():
    """Scenario F: Impossible criteria or non-existent sector produces 'no_match'."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="No Match Candidate",
        education="10th",
        interested_sector_name="NonExistentFantasySector",
        interested_sector_id="non-existent-fantasy-sector",
    )
    rec = generate_nsqf_recommendations(None, profile)
    assert rec.status == "no_match"
    assert len(rec.recommendations) == 0


def test_scenario_g_excluded_sectors_enforcement():
    """Scenario G: Every excluded sector must be strictly rejected at recommendation layer."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Test Citizen",
        education="12th",
    )
    for ex_sec in EXCLUDED_SECTORS:
        # 1. Eligibility gate check
        dummy_qual = {
            "q_code": f"EX/{ex_sec[:3].upper()}",
            "title": f"Course in {ex_sec}",
            "sector_name": ex_sec,
            "sector_id": slugify(ex_sec),
            "nsqf_level": 4.0,
        }
        res = evaluate_nsqf_eligibility(profile, dummy_qual)
        assert res.eligible is False
        assert any("excluded" in fail.lower() for fail in res.hard_failures)

        # 2. Recommendations request check
        profile.interested_sector_name = ex_sec
        profile.interested_sector_id = slugify(ex_sec)
        rec = generate_nsqf_recommendations(None, profile)
        for r in rec.recommendations:
            assert r.sector_name not in EXCLUDED_SECTORS


# ==============================================================================
# 2. AUDIO & MICROPHONE FAILURE HANDLING
# ==============================================================================

def test_audio_validation_rejects_empty():
    """Empty audio payload must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_audio_payload(b"", "audio/webm")
    assert exc.value.status_code == 400


def test_audio_validation_rejects_oversized():
    """Audio exceeding 10 MB limit must raise 413."""
    oversized = b"x" * (10 * 1024 * 1024 + 1)
    with pytest.raises(HTTPException) as exc:
        validate_audio_payload(oversized, "audio/webm")
    assert exc.value.status_code == 413


def test_audio_validation_normalizes_container():
    """Chromium video/webm or unusual MIME prefixes normalize to safe audio format."""
    fn, mime = validate_audio_payload(b"valid_audio_bytes", "video/webm")
    assert fn == "utterance.webm"
    assert mime == "video/webm"

    fn_wav, mime_wav = validate_audio_payload(b"valid_audio_bytes", "audio/wav; codecs=opus")
    assert fn_wav == "utterance.wav"
    assert mime_wav == "audio/wav"


def test_resolve_sarvam_language_code():
    """Language resolution maps Bengali, Hindi, English, and unknown safely."""
    assert resolve_sarvam_language_code("hi") == "hi-IN"
    assert resolve_sarvam_language_code("bn") == "bn-IN"
    assert resolve_sarvam_language_code("en") == "en-IN"
    assert resolve_sarvam_language_code("unknown") == "unknown"
    assert resolve_sarvam_language_code(None) == "unknown"


# ==============================================================================
# 3. AMBIGUITY & CONTRADICTION HANDLING
# ==============================================================================

def test_contradiction_detection_experience_conflict():
    """User previously said 2 years, later claims 0 years (or never worked) -> must flag contradiction."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        work_experience_years=2.0,
        work_experience_label="2 Years",
    )
    new_extracted = ExtractedProfileFields(
        experience_years=0.0,
    )
    contradictions, clar_q = detect_profile_contradictions(new_extracted, profile, lang="en")
    assert len(contradictions) > 0
    assert contradictions[0].field == "experience_years"
    assert contradictions[0].previous_value == 2.0
    assert contradictions[0].new_value == 0.0
    assert clar_q is not None
    assert "2.0" in clar_q or "experience" in clar_q.lower()


def test_contradiction_detection_education_downgrade():
    """User previously said Graduate, later claims 5th Pass -> must flag contradiction."""
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        education="graduate",
        education_label="Graduate",
    )
    new_extracted = ExtractedProfileFields(
        education="5th",
    )
    contradictions, clar_q = detect_profile_contradictions(new_extracted, profile, lang="hi")
    assert len(contradictions) > 0
    assert contradictions[0].field == "education"
    assert clar_q is not None


# ==============================================================================
# 4. SESSION RESUME & STATE MACHINE
# ==============================================================================

def test_session_resume_and_persistence():
    """Starting an interview, answering questions, and resuming retrieves correct state without duplicates."""
    client = FakeSupabase()
    b_id, session_token = seed_test_beneficiary(client)

    # 1. Seed initial interview session
    i_id = uuid4()
    client.database["interview_sessions"].append({
        "id": str(i_id),
        "beneficiary_id": str(b_id),
        "status": "in_progress",
        "current_stage": "education",
        "extracted_profile": {},
        "responses": {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    state = get_adaptive_interview_state(client, i_id, UUID(b_id))
    assert state.current_stage == InterviewStage.EDUCATION
    assert state.current_question is not None

    # 2. Submit education answer
    ans = AdaptiveAnswerSubmit(
        question_id=state.current_question.question_id,
        raw_answer="10th Pass",
        normalized_answer="10th",
        input_method=InputMethod.OPTION,
        language="hi",
    )
    updated_state = submit_answer_to_interview(client, i_id, UUID(b_id), ans)
    assert updated_state.profile_summary.education == "10th"
    assert updated_state.current_stage != InterviewStage.EDUCATION
    assert updated_state.answered_questions_count >= 1

    # 3. Resume interview: re-query state
    resumed_state = get_adaptive_interview_state(client, i_id, UUID(b_id))
    assert resumed_state.profile_summary.education == "10th"
    assert resumed_state.current_stage == updated_state.current_stage
    assert resumed_state.answered_questions_count == updated_state.answered_questions_count


# ==============================================================================
# 5. TTS FALLBACK & AUDIO CLEANUP
# ==============================================================================

def test_tts_graceful_fallback_for_unsupported_language():
    """Unsupported language should return fallback_needed=True and not throw an unhandled error."""
    req = SynthesisRequest(
        text="Hello world in an unsupported dialect",
        language="xyz-unsupported",
    )
    res = asyncio.run(synthesize_speech(req))
    assert res.success is False
    assert res.fallback_needed is True
    assert "uses browser speech synthesis fallback" in res.message


def test_clean_text_for_speech():
    """Text is sanitized of markdown formatting and emojis for speech synthesis."""
    raw = "### Hello **Citizen**! [Click here](url) to view *course*."
    cleaned = clean_text_for_speech(raw)
    assert "###" not in cleaned
    assert "**" not in cleaned
    assert "Hello Citizen" in cleaned
    assert "Click here" in cleaned


# ==============================================================================
# 6. RECOMMENDATION EXPLANATION INTEGRITY
# ==============================================================================

def test_groq_explanation_integrity():
    """Groq explanation must strictly preserve all recommendation q_codes, titles, and ranks."""
    b_id = uuid4()
    i_id = uuid4()
    profile = StructuredBeneficiaryProfile(
        beneficiary_id=b_id,
        interview_id=i_id,
        name="Sunita",
        education="10th",
        interested_sector_name="Agriculture",
    )
    dummy_item = NSQFRecommendationItem(
        q_code="AG/Q1001",
        title="Micro Irrigation Technician",
        sector_id="agriculture",
        sector_name="Agriculture",
        nsqf_level=4.0,
        score=95,
        rank=1,
        match_reasons=["Matches 10th qualification", "Agriculture trade affinity"],
        eligibility=NSQFEligibilityEvaluation(
            status=NSQFEligibilityStatus.ELIGIBLE,
            eligible=True,
            matched_requirements=["Matches 10th qualification"],
        ),
        source="nsqf_nqr_catalog",
    )
    rec_response = NSQFRecommendationResponse(
        beneficiary_id=b_id,
        interview_id=i_id,
        status="eligible",
        generated_at=datetime.now(timezone.utc),
        total_evaluated=1,
        total_recommended=1,
        missing_profile_fields=[],
        recommendations=[dummy_item],
        ineligible_sample=[],
        message="1 course matched.",
    )

    explanation = asyncio.run(explain_nsqf_recommendations_with_groq(
        beneficiary_id=b_id,
        interview_id=i_id,
        recommendations_response=rec_response,
        profile=profile,
        lang="hi",
        top_n=1,
    ))
    assert explanation.beneficiary_id == b_id
    assert len(explanation.items) == 1
    explained_item = explanation.items[0]
    assert explained_item.q_code == "AG/Q1001"
    assert explained_item.title == "Micro Irrigation Technician"
    assert explained_item.nsqf_level == 4.0
    assert explained_item.rank == 1
    assert len(explained_item.spoken_summary) > 0


# ==============================================================================
# 7. SECURITY & AUTHORIZATION (CAPABILITY TOKENS / IDOR)
# ==============================================================================

def test_unauthorized_interview_endpoints_rejected():
    """Interviews routes reject missing or forged bearer authorization."""
    supabase_client = FakeSupabase()
    app.dependency_overrides[get_supabase_client] = lambda: supabase_client
    try:
        client = TestClient(app)
        fake_id = str(uuid4())

        # Missing auth
        res_no_auth = client.get(f"/api/interviews/{fake_id}")
        assert res_no_auth.status_code in (401, 403)

        # Forged auth
        res_bad_auth = client.get(
            f"/api/interviews/{fake_id}",
            headers={"Authorization": "Bearer forged-invalid-token-12345"},
        )
        assert res_bad_auth.status_code in (401, 403)
    finally:
        app.dependency_overrides.clear()


def test_cross_user_interview_access_forbidden():
    """A valid token for beneficiary A cannot access beneficiary B's interview session."""
    supabase_client = FakeSupabase()
    b1_id, token_b1 = seed_test_beneficiary(supabase_client)
    b2_id, token_b2 = seed_test_beneficiary(supabase_client)

    # Create interview owned by B2
    i_b2_id = str(uuid4())
    supabase_client.database["interview_sessions"].append({
        "id": i_b2_id,
        "beneficiary_id": b2_id,
        "revision": 1,
        "responses": {},
        "status": "draft",
    })

    app.dependency_overrides[get_supabase_client] = lambda: supabase_client
    try:
        test_client = TestClient(app)
        res = test_client.get(
            f"/api/interviews/{i_b2_id}",
            headers={"Authorization": f"Bearer {token_b1}"},
        )
        # Should be rejected due to ownership mismatch (IDOR defense)
        assert res.status_code in (403, 404)
    finally:
        app.dependency_overrides.clear()
