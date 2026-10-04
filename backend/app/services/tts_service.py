"""
Utthan Backend - Multilingual Text-to-Speech (TTS) Service.
Proxies synthesis requests to Sarvam AI Bulbul:v3 Indic Voice API.
API credentials remain strictly backend-only. Never exposed to browser clients.
Provides graceful fallbacks if network is offline or language is not supported.
"""

import logging
import re
from typing import Optional
import httpx

from app.core.config import settings
from app.schemas.voice import SynthesisRequest, SynthesisResponse

logger = logging.getLogger("utthan.tts")

# Mapping of application language codes to Sarvam Bulbul:v3 supported BCP-47 codes
SARVAM_TTS_LANG_MAP = {
    "hi": "hi-IN",
    "bn": "bn-IN",
    "te": "te-IN",
    "ta": "ta-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "or": "od-IN",
    "pa": "pa-IN",
    "en": "en-IN",
}

# Maximum character length per Sarvam synthesis chunk
MAX_TTS_TEXT_LENGTH = 450


def clean_text_for_speech(text: str) -> str:
    """Removes Markdown characters, emojis, and special symbols for natural pronunciation."""
    if not text:
        return ""
    # Strip markdown symbols
    cleaned = re.sub(r'[*_#`~\[\]()]', '', text)
    # Strip excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def resolve_sarvam_tts_language(lang_code: Optional[str]) -> Optional[str]:
    """Resolves language code to Sarvam TTS target code if supported."""
    if not lang_code:
        return "hi-IN"
    clean = lang_code.strip().lower().split("-")[0]
    return SARVAM_TTS_LANG_MAP.get(clean)


async def synthesize_speech(payload: SynthesisRequest) -> SynthesisResponse:
    """
    Synthesizes speech using Sarvam AI Indic TTS API.
    If Sarvam is unconfigured, language unsupported, or request fails, returns
    fallback_needed=True to allow the frontend to gracefully use browser TTS or text.
    """
    clean_text = clean_text_for_speech(payload.text)
    if not clean_text:
        return SynthesisResponse(
            audio_base64=None,
            language_code=payload.language,
            success=False,
            fallback_needed=True,
            message="No text content to synthesize.",
        )

    target_lang = resolve_sarvam_tts_language(payload.language)
    if not target_lang:
        logger.info(
            "Language '%s' not natively in Sarvam Bulbul:v3; signaling browser speech fallback",
            payload.language
        )
        return SynthesisResponse(
            audio_base64=None,
            language_code=payload.language,
            success=False,
            fallback_needed=True,
            message=f"Language '{payload.language}' uses browser speech synthesis fallback.",
        )

    if not settings.is_sarvam_configured:
        logger.warning("Sarvam API key not configured; signaling fallback")
        return SynthesisResponse(
            audio_base64=None,
            language_code=target_lang,
            success=False,
            fallback_needed=True,
            message="Sarvam TTS service unconfigured in backend.",
        )

    # Chunk text to avoid provider overflow
    chunk = clean_text[:MAX_TTS_TEXT_LENGTH]
    tts_url = getattr(settings, "SARVAM_TTS_URL", "https://api.sarvam.ai/text-to-speech")

    valid_speakers = {
        "aditya", "ritu", "ashutosh", "priya", "neha", "rahul", "pooja", "rohan",
        "simran", "kavya", "amit", "dev", "ishita", "shreya", "ratan", "varun",
        "manan", "sumit", "roopa", "kabir", "aayan", "shubh", "advait", "anand",
        "tanya", "tarun", "sunny", "mani", "gokul", "vijay", "shruti", "suhani",
        "mohit", "kavitha", "rehan", "soham", "rupali",
    }
    req_speaker = (payload.speaker or getattr(settings, "SARVAM_TTS_SPEAKER", "ritu")).strip().lower()
    selected_speaker = req_speaker if req_speaker in valid_speakers else "ritu"

    request_body = {
        "inputs": [chunk],
        "target_language_code": target_lang,
        "speaker": selected_speaker,
        "pitch": 0,
        "pace": payload.pace or 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 22050,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                tts_url,
                headers={
                    "api-subscription-key": settings.SARVAM_API_KEY,
                    "Content-Type": "application/json",
                },
                json=request_body,
            )

            if resp.status_code == 200:
                data = resp.json()
                audios = data.get("audios", [])
                if audios and len(audios) > 0 and audios[0]:
                    return SynthesisResponse(
                        audio_base64=audios[0],
                        content_type="audio/wav",
                        language_code=target_lang,
                        provider="sarvam",
                        success=True,
                        fallback_needed=False,
                    )
                else:
                    logger.warning("Sarvam TTS returned 200 but empty audio list")
            else:
                logger.warning("Sarvam TTS returned status %d: %s", resp.status_code, resp.text[:120])

    except httpx.TimeoutException:
        logger.warning("Sarvam TTS request timed out")
    except Exception as exc:
        logger.warning("Sarvam TTS request failed: %s", exc)

    return SynthesisResponse(
        audio_base64=None,
        language_code=target_lang,
        provider="sarvam",
        success=False,
        fallback_needed=True,
        message="Sarvam TTS unavailable; client should use Web Speech fallback.",
    )
