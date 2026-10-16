from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings


def _engine():
    settings = get_settings()
    url = settings.database_url
    connect_args: dict = {}
    kwargs: dict = {
        "echo": settings.app_env == "development",
        "pool_pre_ping": True,
    }
    # Supabase PgBouncer transaction pooler: no prepared statements; NullPool (PgBouncer pools).
    if "pooler.supabase.com" in url or ":6543/" in url:
        connect_args["statement_cache_size"] = 0
        kwargs["poolclass"] = NullPool
        kwargs.pop("pool_pre_ping", None)
    if connect_args:
        kwargs["connect_args"] = connect_args
    return create_async_engine(url, **kwargs)


engine = _engine()
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
