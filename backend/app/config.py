from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = "RTGS API"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    database_url: str = "sqlite+aiosqlite:///./rtgs_dev.db"

    supabase_url: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_jwks_url: Optional[str] = None
    jwt_audience: str = "authenticated"
    jwt_issuer: Optional[str] = None
    jwt_algorithms: str = "HS256,ES256,RS256"

    supabase_storage_bucket: str = "complaint-attachments"
    attachment_max_bytes: int = 5_242_880
    attachment_allowed_content_types: str = "image/jpeg,image/png,image/webp,application/pdf"
    signed_url_ttl_seconds: int = 900

    grievance_ref_prefix: str = "RTGS"
    reopen_window_days: int = 30

    ai_mode: Literal["rules", "llm", "hybrid"] = "rules"
    openai_api_key: Optional[str] = None
    ai_model: Optional[str] = None
    ai_request_timeout_seconds: int = 25
    ai_vision_provider: Optional[str] = None

    auth_dev_bypass: bool = False
    auth_dev_user_id: Optional[str] = None
    auth_dev_role: str = "citizen"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def jwt_algorithm_list(self) -> list[str]:
        return [a.strip() for a in self.jwt_algorithms.split(",") if a.strip()]

    @property
    def allowed_attachment_types(self) -> set[str]:
        return {t.strip().lower() for t in self.attachment_allowed_content_types.split(",") if t.strip()}

    @property
    def resolved_jwks_url(self) -> Optional[str]:
        if self.supabase_jwt_jwks_url:
            return self.supabase_jwt_jwks_url
        if self.supabase_url:
            return f"{self.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()
