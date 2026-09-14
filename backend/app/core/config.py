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
