"""
Tests for Utthan Multilingual Voice / STT Service and Routes
"""

import io
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from starlette.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.services.stt_service import (
    resolve_sarvam_language_code,
    validate_audio_payload,
    transcribe_audio,
)

client = TestClient(app)


def test_language_code_resolution():
    """Verify application language IDs map to correct Sarvam BCP-47 codes."""
    assert resolve_sarvam_language_code("hi") == "hi-IN"
    assert resolve_sarvam_language_code("bn") == "bn-IN"
    assert resolve_sarvam_language_code("or") == "od-IN"
    assert resolve_sarvam_language_code("dgo") == "doi-IN"
    assert resolve_sarvam_language_code("en") == "en-IN"
    assert resolve_sarvam_language_code("te") == "te-IN"
    assert resolve_sarvam_language_code("hi-IN") == "hi-IN"
    assert resolve_sarvam_language_code("unknown") == "unknown"
    assert resolve_sarvam_language_code(None) == "unknown"
    assert resolve_sarvam_language_code("xyz_nonexistent") == "unknown"


def test_audio_validation_rejects_empty():
    """Empty audio payload should raise 400."""
    with pytest.raises(Exception) as excinfo:
        validate_audio_payload(b"", "audio/webm")
    assert "empty" in str(excinfo.value.detail).lower()


def test_audio_validation_rejects_oversized():
    """Audio exceeding 10MB should raise 413."""
    huge_payload = b"0" * (10 * 1024 * 1024 + 1)
    with pytest.raises(Exception) as excinfo:
        validate_audio_payload(huge_payload, "audio/webm")
    assert excinfo.value.status_code == 413


def test_audio_validation_detects_container_extension():
    """Verify container extension detection."""
    filename, ct = validate_audio_payload(b"fake_data", "audio/wav")
    assert filename == "utterance.wav"
    assert ct == "audio/wav"

    filename, ct = validate_audio_payload(b"fake_data", "audio/webm;codecs=opus")
    assert filename == "utterance.webm"
    assert ct == "audio/webm"


def test_transcribe_unconfigured_sarvam_returns_503(monkeypatch):
    """When SARVAM_API_KEY is missing or placeholder, returns 503."""
    monkeypatch.setattr(settings, "SARVAM_API_KEY", "")
    response = client.post(
        "/api/voice/transcribe",
        files={"file": ("test.webm", b"audio_dummy_content", "audio/webm")},
        data={"language": "hi"},
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()


def test_transcribe_successful_mock(monkeypatch):
    """Successful transcription with mocked Sarvam API response."""
    import asyncio
    monkeypatch.setattr(settings, "SARVAM_API_KEY", "sk_mock_valid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        200,
        json={
            "request_id": "req-12345",
            "transcript": "नमस्ते मैं सिलाई का काम सीखना चाहता हूँ",
            "language_code": "hi-IN",
        },
        request=httpx.Request("POST", "https://api.sarvam.ai/speech-to-text"),
    )
    mock_client.post.return_value = mock_response

    result = asyncio.run(
        transcribe_audio(
            audio_bytes=b"dummy_recorded_audio_bytes",
            content_type="audio/webm",
            language_hint="hi",
            client=mock_client,
        )
    )

    assert result.transcript == "नमस्ते मैं सिलाई का काम सीखना चाहता हूँ"
    assert result.language_code == "hi-IN"
    assert result.model == settings.SARVAM_STT_MODEL


def test_transcribe_timeout_handling(monkeypatch):
    """Timeout during provider call returns 504."""
    import asyncio
    monkeypatch.setattr(settings, "SARVAM_API_KEY", "sk_mock_valid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.side_effect = httpx.TimeoutException("Connection timed out")

    with pytest.raises(Exception) as excinfo:
        asyncio.run(
            transcribe_audio(
                audio_bytes=b"dummy_recorded_audio_bytes",
                content_type="audio/webm",
                language_hint="bn",
                client=mock_client,
            )
        )

    assert excinfo.value.status_code == 504
    assert "timed out" in excinfo.value.detail.lower()


def test_transcribe_auth_failure_sanitized(monkeypatch):
    """Provider 401 returns sanitized 502 without leaking key."""
    import asyncio
    monkeypatch.setattr(settings, "SARVAM_API_KEY", "sk_mock_invalid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        401,
        text="Unauthorized invalid key",
        request=httpx.Request("POST", "https://api.sarvam.ai/speech-to-text"),
    )
    mock_client.post.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        asyncio.run(
            transcribe_audio(
                audio_bytes=b"dummy_recorded_audio_bytes",
                content_type="audio/webm",
                language_hint="hi",
                client=mock_client,
            )
        )

    assert excinfo.value.status_code == 502
    assert "authentication failed" in excinfo.value.detail.lower()
    assert "sk_mock" not in excinfo.value.detail



def test_transcribe_endpoint_integration(monkeypatch):
    """Test full endpoint POST /api/voice/transcribe with patched service."""
    from app.schemas.voice import TranscriptionResponse

    async def mock_transcribe(*args, **kwargs):
        return TranscriptionResponse(
            transcript="বাংলা ভাষা নির্বাচন করা হলো",
            language_code="bn-IN",
            model="saaras:v4",
        )

    with patch("app.api.routes.voice.transcribe_audio", side_effect=mock_transcribe):
        audio_file = io.BytesIO(b"fake_webm_audio_stream")
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("speech.webm", audio_file, "audio/webm")},
            data={"language": "bn"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transcript"] == "বাংলা ভাষা নির্বাচন করা হলো"
        assert data["language_code"] == "bn-IN"
        assert data["model"] == "saaras:v4"
