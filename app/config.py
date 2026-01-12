from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # API Configuration
    api_key: str
    api_title: str = "Code Check API"
    api_version: str = "1.0.0"
    api_description: str = "AI-powered zoning and sign code research API"

    # AI Service API Keys
    perplexity_api_key: str
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Supabase Configuration (Phase 1+)
    supabase_url: Optional[str] = None
    supabase_project_id: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    # Default LLM Provider
    default_llm_provider: str = "openai"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables

settings = Settings()
