"""
Utthan Backend - Multilingual Speech-to-Text (STT) Service
Proxies audio securely to Sarvam AI (saaras:v4) without exposing credentials to the browser.
Audio is processed transiently in-memory with zero disk persistence.
"""

import logging
from typing import Optional, Tuple
import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.voice import TranscriptionResponse

logger = logging.getLogger("utthan.stt")

# Maximum permitted audio upload size (10 MB)
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024

# Mapping from Utthan internal language identifiers to Sarvam BCP-47 codes
SARVAM_STT_LANG_MAP = {
    "hi": "hi-IN",
    "bn": "bn-IN",
    "te": "te-IN",
    "mr": "mr-IN",
    "ta": "ta-IN",
    "ur": "ur-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "or": "od-IN",
    "pa": "pa-IN",
    "as": "as-IN",
    "mai": "mai-IN",
    "sa": "sa-IN",
    "ne": "ne-IN",
    "kok": "kok-IN",
    "sd": "sd-IN",
    "ks": "ks-IN",
    "dgo": "doi-IN",
    "mni": "mni-IN",
    "brx": "brx-IN",
    "sat": "sat-IN",
    "en": "en-IN",
}

# Permitted audio MIME types from browser recording
SUPPORTED_MIME_PREFIXES = (
    "audio/",
    "video/webm",  # Some Chromium browsers record WebM audio with video/webm container
)


def resolve_sarvam_language_code(language_hint: Optional[str]) -> str:
    """
    Resolves an application language identifier or BCP-47 hint into a Sarvam-compatible code.
    If no hint or unknown language is passed, returns 'unknown' for automatic provider detection.
    """
    if not language_hint:
        return "unknown"

    cleaned = language_hint.strip().lower()
    if cleaned in SARVAM_STT_LANG_MAP:
        return SARVAM_STT_LANG_MAP[cleaned]

    # Check if already BCP-47 (e.g., 'hi-in', 'bn-in')
    for code in SARVAM_STT_LANG_MAP.values():
        if cleaned == code.lower():
            return code

    if cleaned == "unknown" or cleaned == "auto":
        return "unknown"

    # Default to auto-detection if unrecognized
    return "unknown"


def validate_audio_payload(audio_bytes: bytes, content_type: Optional[str]) -> Tuple[str, str]:
    """
    Validates audio byte payload size and returns (filename, mime_type).
    Raises HTTPException for empty or oversized payloads.
    """
    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio recording is empty. Please speak into the microphone."
        )

    if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio recording exceeds the maximum permitted size (10 MB)."
        )

    ct = (content_type or "audio/webm").split(";")[0].strip().lower()
    if not any(ct.startswith(prefix) for prefix in SUPPORTED_MIME_PREFIXES):
        # Fallback to audio/webm if unrecognized container
        ct = "audio/webm"

    extension = "webm"
    if "wav" in ct:
        extension = "wav"
    elif "mp4" in ct or "m4a" in ct:
        extension = "m4a"
    elif "ogg" in ct or "opus" in ct:
        extension = "ogg"
    elif "mpeg" in ct or "mp3" in ct:
        extension = "mp3"

    filename = f"utterance.{extension}"
    return filename, ct


async def transcribe_audio(
    audio_bytes: bytes,
    content_type: Optional[str] = None,
    language_hint: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> TranscriptionResponse:
    """
    Transcribes audio bytes via Sarvam AI Speech-to-Text API.
    Processes audio strictly in-memory without persistent disk caching.
    """
    if not settings.is_sarvam_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice recognition service is not configured on the server."
        )

    filename, mime_type = validate_audio_payload(audio_bytes, content_type)
    sarvam_lang = resolve_sarvam_language_code(language_hint)

    files = {
        "file": (filename, audio_bytes, mime_type),
    }
    data = {
        "model": settings.SARVAM_STT_MODEL,
        "language_code": sarvam_lang,
        "mode": "transcribe",
    }
    headers = {
        "api-subscription-key": settings.SARVAM_API_KEY,
    }

    should_close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=settings.SARVAM_STT_TIMEOUT_SECONDS)
        should_close_client = True

    try:
        response = await client.post(
            settings.SARVAM_STT_URL,
            headers=headers,
            data=data,
            files=files,
        )
    except httpx.TimeoutException:
        logger.warning("Sarvam STT request timed out after %s seconds", settings.SARVAM_STT_TIMEOUT_SECONDS)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Voice recognition request timed out. Please try speaking again."
        )
    except httpx.RequestError as exc:
        logger.error("Sarvam STT network communication failure: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to reach the voice recognition service. Please check your network connection."
        )
    finally:
        if should_close_client:
            await client.aclose()

    if response.status_code == 200:
        try:
            payload = response.json()
            raw_transcript = payload.get("transcript", "")
            detected_lang = payload.get("language_code", sarvam_lang)
            return TranscriptionResponse(
                transcript=raw_transcript.strip(),
                language_code=detected_lang,
                model=settings.SARVAM_STT_MODEL,
            )
        except Exception as parse_err:
            logger.error("Failed to parse Sarvam STT JSON response: %s", str(parse_err))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unexpected response format from voice recognition service."
            )

    # Provider error handling with sanitized messages (never leak API key)
    logger.warning("Sarvam STT returned error HTTP %s: %s", response.status_code, response.text[:200])

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Voice recognition service authentication failed. Please verify server configuration."
        )
    elif response.status_code == 400:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The voice recognition service could not process the provided audio format."
        )
    elif response.status_code == 429:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Voice recognition service rate limit reached. Please wait a moment and try again."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Voice recognition service is temporarily unavailable. Please try again."
        )
