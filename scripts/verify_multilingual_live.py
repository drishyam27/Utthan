"""
Verify multilingual voice pipeline live: Bengali, Hindi, English.
Tests:
1. Sarvam TTS live generation for bn, hi, en.
2. Sarvam STT live transcription of generated audio.
3. Groq conversational interpretation in bn, hi, en.
"""

import sys
import asyncio
import base64
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.core.config import settings
from app.services.stt_service import transcribe_audio
from app.services.tts_service import synthesize_speech
from app.services.groq_service import call_groq_chat_completion
from app.schemas.voice import SynthesisRequest

TEST_PHRASES = {
    "hi": {
        "text": "मैंने दसवीं कक्षा पास की है और मैं खेती का काम करता हूँ।",
        "lang_code": "hi",
    },
    "bn": {
        "text": "আমি দশম শ্রেণি পাস করেছি এবং আমি কৃষি কাজ করতে চাই।",
        "lang_code": "bn",
    },
    "en": {
        "text": "I have completed tenth grade and I want to work in agriculture.",
        "lang_code": "en",
    },
}

async def test_multilingual():
    print("==================================================")
    print("LIVE MULTILINGUAL PIPELINE VERIFICATION (HI, BN, EN)")
    print("==================================================")

    results = {}
    for lang, data in TEST_PHRASES.items():
        print(f"\n--- Testing Language: {lang.upper()} ---")
        text = data["text"]
        
        # 1. TTS
        tts_req = SynthesisRequest(text=text, language=lang)
        tts_res = await synthesize_speech(tts_req)
        tts_success = tts_res.success and bool(tts_res.audio_base64)
        print(f"  TTS Synthesis: {'SUCCESS' if tts_success else 'FAILED'} (Format: {tts_res.content_type}, Audio size: {len(tts_res.audio_base64 or '')})")

        # 2. STT
        stt_success = False
        transcribed_text = ""
        if tts_success:
            audio_bytes = base64.b64decode(tts_res.audio_base64)
            stt_res = await transcribe_audio(
                audio_bytes=audio_bytes,
                content_type=tts_res.content_type,
                language_hint=lang,
            )
            transcribed_text = stt_res.transcript
            stt_success = bool(transcribed_text)
            print(f"  STT Transcription: {'SUCCESS' if stt_success else 'FAILED'} (Detected: '{stt_res.language_code}')")
            print(f"  Transcribed: {transcribed_text}")

        # 3. Groq Interpretation
        groq_success = False
        if stt_success:
            messages = [
                {
                    "role": "system",
                    "content": "You are a skilling intake assistant. Extract education and sector in JSON format: {\"education\": string, \"sector\": string}",
                },
                {"role": "user", "content": transcribed_text},
            ]
            groq_res = await call_groq_chat_completion(messages)
            extracted = groq_res.get("choices", [{}])[0].get("message", {}).get("content", "")
            groq_success = bool(extracted)
            print(f"  Groq Structured Extraction: {'SUCCESS' if groq_success else 'FAILED'}")
            print(f"  Extracted JSON: {extracted.strip()}")

        results[lang] = {
            "tts": tts_success,
            "stt": stt_success,
            "groq": groq_success,
        }

    print("\n==================================================")
    print("MULTILINGUAL SUMMARY:")
    for lang, r in results.items():
        all_ok = all(r.values())
        print(f"  {lang.upper()}: {'LIVE TESTED - 100% PASS' if all_ok else 'PARTIAL/FAILED'} (TTS={r['tts']}, STT={r['stt']}, Groq={r['groq']})")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_multilingual())
