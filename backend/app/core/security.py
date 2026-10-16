from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import unauthorized
from app.models.entities import Profile
from app.models.enums import UserRole


@dataclass
class AuthUser:
    id: UUID
    email: str
    role: UserRole
    is_active: bool


def decode_supabase_token(token: str) -> dict:
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        raise unauthorized("JWT verification not configured")
    options = {"verify_aud": bool(settings.jwt_audience)}
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_audience if settings.jwt_audience else None,
            issuer=settings.jwt_issuer if settings.jwt_issuer else None,
            options=options,
        )
    except JWTError as exc:
        raise unauthorized("Invalid or expired token") from exc
    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise unauthorized("Token expired")
    return payload


async def resolve_user_from_token(db: AsyncSession, token: str | None) -> AuthUser:
    settings = get_settings()
    if settings.auth_dev_bypass and settings.auth_dev_user_id:
        user_id = UUID(settings.auth_dev_user_id)
        profile = await db.get(Profile, user_id)
        if not profile:
            raise unauthorized("Dev bypass user not found in database")
        return AuthUser(
            id=profile.id,
            email=profile.email,
            role=UserRole(profile.role),
            is_active=profile.is_active,
        )
    if not token:
        raise unauthorized("Missing bearer token")
    payload = decode_supabase_token(token)
    sub = payload.get("sub")
    if not sub:
        raise unauthorized("Invalid token subject")
    user_id = UUID(sub)
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()
    if not profile or not profile.is_active:
        raise unauthorized("User profile not found or inactive")
    return AuthUser(
        id=profile.id,
        email=profile.email,
        role=UserRole(profile.role),
        is_active=profile.is_active,
    )
