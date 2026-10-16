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
    jwt_audience: str = "authenticated"
    jwt_issuer: Optional[str] = None

    grievance_ref_prefix: str = "RTGS"

    # Test / local dev bypass (never enable in production)
    auth_dev_bypass: bool = False
    auth_dev_user_id: Optional[str] = None
    auth_dev_role: str = "citizen"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
