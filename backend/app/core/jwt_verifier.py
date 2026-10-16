from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from jose import JWTError, jwk, jwt
from app.config import get_settings
from app.core.exceptions import unauthorized

logger = logging.getLogger("rtgs.jwt")

_jwks_cache: dict[str, Any] | None = None
_jwks_fetched_at: datetime | None = None
_JWKS_TTL_SECONDS = 3600


async def _fetch_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_fetched_at
    settings = get_settings()
    url = settings.resolved_jwks_url
    if not url:
        raise unauthorized("JWKS URL not configured")
    now = datetime.now(timezone.utc)
    if _jwks_cache and _jwks_fetched_at and (now - _jwks_fetched_at).total_seconds() < _JWKS_TTL_SECONDS:
        return _jwks_cache
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_fetched_at = now
        return _jwks_cache


def _decode_hs256(token: str, secret: str) -> dict:
    settings = get_settings()
    return jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        audience=settings.jwt_audience if settings.jwt_audience else None,
        issuer=settings.jwt_issuer if settings.jwt_issuer else None,
        options={"verify_aud": bool(settings.jwt_audience)},
    )


async def _decode_asymmetric(token: str) -> dict:
    settings = get_settings()
    header = jwt.get_unverified_header(token)
    alg = header.get("alg")
    if alg not in settings.jwt_algorithm_list:
        raise unauthorized("Unsupported JWT algorithm")
    jwks = await _fetch_jwks()
    kid = header.get("kid")
    keys = jwks.get("keys", [])
    key_data = next((k for k in keys if k.get("kid") == kid), None)
    if not key_data and keys:
        key_data = keys[0]
    if not key_data:
        raise unauthorized("JWT signing key not found")
    public_key = jwk.construct(key_data)
    return jwt.decode(
        token,
        public_key,
        algorithms=[alg],
        audience=settings.jwt_audience if settings.jwt_audience else None,
        issuer=settings.jwt_issuer if settings.jwt_issuer else None,
        options={"verify_aud": bool(settings.jwt_audience)},
    )


async def verify_supabase_jwt(token: str) -> dict:
    settings = get_settings()
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise unauthorized("Malformed token") from exc
    alg = header.get("alg", "HS256")
    try:
        if alg == "HS256":
            if not settings.supabase_jwt_secret:
                raise unauthorized("JWT secret not configured for HS256")
            payload = _decode_hs256(token, settings.supabase_jwt_secret)
        else:
            payload = await _decode_asymmetric(token)
    except JWTError as exc:
        logger.info("JWT validation failed: %s", exc.__class__.__name__)
        raise unauthorized("Invalid or expired token") from exc
    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise unauthorized("Token expired")
    return payload


def reset_jwks_cache_for_tests() -> None:
    global _jwks_cache, _jwks_fetched_at
    _jwks_cache = None
    _jwks_fetched_at = None
