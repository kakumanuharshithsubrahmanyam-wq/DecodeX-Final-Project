from __future__ import annotations

import pytest
from jose import jwt

from app.config import get_settings
from app.core.jwt_verifier import verify_supabase_jwt, reset_jwks_cache_for_tests


@pytest.mark.asyncio
async def test_hs256_jwt_roundtrip(monkeypatch):
    secret = "test-secret-for-jwt-only"
    get_settings.cache_clear()
    monkeypatch.setenv("SUPABASE_JWT_SECRET", secret)
    monkeypatch.setenv("JWT_AUDIENCE", "authenticated")
    monkeypatch.setenv("JWT_ISSUER", "")
    monkeypatch.setenv("AUTH_DEV_BYPASS", "false")
    get_settings.cache_clear()
    reset_jwks_cache_for_tests()
    token = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000001", "aud": "authenticated", "exp": 9999999999},
        secret,
        algorithm="HS256",
    )
    payload = await verify_supabase_jwt(token)
    assert payload["sub"] == "00000000-0000-0000-0000-000000000001"
