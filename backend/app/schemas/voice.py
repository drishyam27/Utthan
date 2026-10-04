"""
Utthan Backend - Voice & Speech-to-Text Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    """Normalized response for voice transcription."""
    transcript: str = Field(..., description="Recognized transcript from speech audio")
    language_code: Optional[str] = Field(None, description="BCP-47 language code detected or used")
    model: Optional[str] = Field(None, description="STT model used for transcription")


class SynthesisRequest(BaseModel):
    """Payload for text-to-speech synthesis request."""
    text: str = Field(..., description="Text content to synthesize into speech")
    language: str = Field(default="hi", description="Language code (e.g. 'hi', 'bn', 'en', 'hi-IN')")
    speaker: Optional[str] = Field(default="ritu", description="Voice profile (e.g. 'ritu', 'priya', 'aditya')")
    pace: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech rate multiplier")


class SynthesisResponse(BaseModel):
    """Response containing synthesized audio or fallback indicator."""
    audio_base64: Optional[str] = Field(None, description="Base64-encoded WAV audio data")
    content_type: str = Field(default="audio/wav", description="MIME type of returned audio")
    language_code: str = Field(..., description="Language code used for synthesis")
    provider: str = Field(default="sarvam", description="TTS engine name")
    success: bool = Field(default=True, description="True if audio was successfully synthesized")
    fallback_needed: bool = Field(default=False, description="True if client should fall back to browser Web Speech")
    message: Optional[str] = Field(None, description="Informational message or failure reason")

