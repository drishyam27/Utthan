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
