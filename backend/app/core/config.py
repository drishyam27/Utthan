"""
Utthan Platform - Core Configuration
Loads environment variables safely and provides structured application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in backend directory, then project root
backend_dir = Path(__file__).resolve().parent.parent.parent
env_candidates = [
    backend_dir / ".env",
    backend_dir.parent / ".env",
]

for env_path in env_candidates:
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path)
        break


class Settings:
    """Application settings resolved from environment variables."""
    PROJECT_NAME: str = "Utthan API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Supabase credentials (Service Role for backend-only elevated access)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    
    # Frontend origin for CORS
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").strip()

    # Location resolution provider. Nominatim is a development-compatible,
    # configurable default; production deployments should select an approved
    # provider and review its usage policy before enabling it.
    LOCATION_PROVIDER: str = os.getenv("LOCATION_PROVIDER", "nominatim").strip().lower()
    LOCATION_REVERSE_GEOCODER_URL: str = os.getenv(
        "LOCATION_REVERSE_GEOCODER_URL",
        "https://nominatim.openstreetmap.org/reverse"
    ).strip()
    LOCATION_PROVIDER_USER_AGENT: str = os.getenv(
        "LOCATION_PROVIDER_USER_AGENT",
        "Utthan/2B location resolver"
    ).strip()
    LOCATION_PROVIDER_TIMEOUT_SECONDS: float = float(
        os.getenv("LOCATION_PROVIDER_TIMEOUT_SECONDS", "8")
    )

    # Sarvam AI STT Configuration
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "").strip()
    SARVAM_STT_URL: str = os.getenv(
        "SARVAM_STT_URL",
        "https://api.sarvam.ai/speech-to-text"
    ).strip()
    SARVAM_STT_MODEL: str = os.getenv("SARVAM_STT_MODEL", "saaras:v4").strip()
    SARVAM_STT_TIMEOUT_SECONDS: float = float(
        os.getenv("SARVAM_STT_TIMEOUT_SECONDS", "15")
    )
    SARVAM_TTS_URL: str = os.getenv(
        "SARVAM_TTS_URL",
        "https://api.sarvam.ai/text-to-speech"
    ).strip()


    # Groq LLM Conversational Understanding Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()
    GROQ_TIMEOUT_SECONDS: float = float(
        os.getenv("GROQ_TIMEOUT_SECONDS", "12.0")
    )

    @property
    def is_groq_configured(self) -> bool:
        """Returns True if Groq API key is provided and non-placeholder."""
        if not self.GROQ_API_KEY or "your_groq" in self.GROQ_API_KEY or len(self.GROQ_API_KEY) < 10:
            return False
        return True

    @property
    def is_sarvam_configured(self) -> bool:
        """Returns True if Sarvam API key is provided and non-placeholder."""
        if not self.SARVAM_API_KEY or "your_sarvam" in self.SARVAM_API_KEY:
            return False
        return True

    @property
    def is_supabase_configured(self) -> bool:
        """Returns True if Supabase credentials are provided and non-placeholder."""
        if not self.SUPABASE_URL or not self.SUPABASE_SERVICE_ROLE_KEY:
            return False
        if "your-project-id" in self.SUPABASE_URL or "your_supabase" in self.SUPABASE_SERVICE_ROLE_KEY:
            return False
        return True

    @property
    def allowed_origins(self) -> list[str]:
        """Parsed list of allowed CORS origins."""
        origins = [self.FRONTEND_ORIGIN]
        # Include common local development ports for developer ergonomics
        local_defaults = ["http://localhost:5173", "http://127.0.0.1:5173"]
        for origin in local_defaults:
            if origin not in origins:
                origins.append(origin)
        return origins


settings = Settings()
