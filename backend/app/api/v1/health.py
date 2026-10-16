from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app import __version__
from app.api.deps import DbSession
from app.config import get_settings
from app.schemas.common import DataResponse

router = APIRouter()


@router.get("/health")
async def health(db: DbSession) -> dict:
    settings = get_settings()
    db_status = "unknown"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"
    return {
        "data": {
            "status": "ok" if db_status == "ok" else "degraded",
            "service": settings.app_name,
            "version": __version__,
            "database": db_status,
        }
    }
