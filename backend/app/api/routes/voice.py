"""
Utthan Backend - Voice API Routes
Provides endpoints for audio transcription via Sarvam AI STT.
"""

from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.voice import TranscriptionResponse
from app.services.stt_service import transcribe_audio

router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    summary="Transcribe audio to text",
    description=(
        "Accepts recorded audio from citizen microphone and returns text transcript "
        "using Sarvam AI multilingual Speech-to-Text. Processes audio in-memory."
    ),
)
async def transcribe_voice(
    file: UploadFile = File(..., description="Recorded audio file (WebM, WAV, OGG, etc.)"),
    language: Optional[str] = Form(None, description="Optional language hint (e.g. 'hi', 'bn', or 'hi-IN')"),
) -> TranscriptionResponse:
    """
    Transcribes uploaded audio blob and returns the transcribed text.
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file was uploaded."
        )

    try:
        audio_bytes = await file.read()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read audio data."
        )

    return await transcribe_audio(
        audio_bytes=audio_bytes,
        content_type=file.content_type,
        language_hint=language,
    )
