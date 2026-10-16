from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthUser, resolve_user_from_token
from app.db.session import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    authorization: Annotated[Optional[str], Header()] = None,
) -> AuthUser:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    return await resolve_user_from_token(db, token)


CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
