"""
Test live provider connectivity: Groq API, Sarvam STT, Sarvam TTS.
Does NOT log or print raw API keys.
"""

import sys
import asyncio
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

# Force utf-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.core.config import settings
from app.services.groq_service import call_groq_chat_completion
from app.services.stt_service import transcribe_audio
from app.services.tts_service import synthesize_speech
from app.schemas.voice import SynthesisRequest

async def test_live_groq():
    print("Testing live Groq API...")
    if not settings.is_groq_configured:
        print("  Groq API is NOT configured.")
        return False
    try:
        messages = [
            {"role": "system", "content": "You are a public skilling assistant. Respond strictly in JSON: {\"status\": \"ok\", \"message\": string}"},
            {"role": "user", "content": "Hello! Confirm connectivity for Utthan testing."},
        ]
        res = await call_groq_chat_completion(messages)
        content = res.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"  Groq Live Chat Completion: Success! (Response: {content.strip()})")
        return True
    except Exception as e:
        print(f"  Groq Live Test Failed: {e}")
        return False

async def test_live_sarvam_tts():
    print("\nTesting live Sarvam TTS...")
    if not settings.is_sarvam_configured:
        print("  Sarvam API is NOT configured.")
        return False, None, None
    try:
        req = SynthesisRequest(
            text="नमस्ते, उत्थान में आपका स्वागत है।",
            language="hi",
        )
        res = await synthesize_speech(req)
        if res.success and res.audio_base64:
            print(f"  Sarvam Live TTS: Success! (Audio length: {len(res.audio_base64)} chars, format: {res.content_type})")
            return True, res.audio_base64, res.content_type
        else:
            print(f"  Sarvam Live TTS returned failure: {res.message}")
            return False, None, None
    except Exception as e:
        print(f"  Sarvam Live TTS Exception: {e}")
        return False, None, None

async def test_live_sarvam_stt(audio_b64, audio_format):
    print("\nTesting live Sarvam STT...")
    if not settings.is_sarvam_configured:
        print("  Sarvam API is NOT configured.")
        return False
    if not audio_b64:
        print("  Skipping STT because TTS did not provide test audio.")
        return False
    try:
        import base64
        audio_bytes = base64.b64decode(audio_b64)
        mime = audio_format or "audio/wav"
        res = await transcribe_audio(
            audio_bytes=audio_bytes,
            content_type=mime,
            language_hint="hi",
        )
        print(f"  Sarvam Live STT: Success! Transcribed: '{res.transcript}', Detected Lang: '{res.language_code}'")
        return True
    except Exception as e:
        print(f"  Sarvam Live STT Failed: {e}")
        return False

async def main():
    print("==================================================")
    print("LIVE PROVIDER SANITY VERIFICATION")
    print("==================================================")
    groq_ok = await test_live_groq()
    tts_ok, audio_b64, audio_fmt = await test_live_sarvam_tts()
    stt_ok = await test_live_sarvam_stt(audio_b64, audio_fmt)
    print("\n--------------------------------------------------")
    print(f"Live Provider Summary:")
    print(f"  - Groq API   : {'LIVE TESTED - PASS' if groq_ok else 'FAILED/UNAVAILABLE'}")
    print(f"  - Sarvam TTS : {'LIVE TESTED - PASS' if tts_ok else 'FAILED/UNAVAILABLE'}")
    print(f"  - Sarvam STT : {'LIVE TESTED - PASS' if stt_ok else 'FAILED/UNAVAILABLE'}")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
