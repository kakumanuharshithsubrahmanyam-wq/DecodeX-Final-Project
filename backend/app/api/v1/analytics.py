from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.permissions import is_platform_admin
from app.core.exceptions import forbidden
from app.models.entities import AuditLog
from app.services.analytics import overview

router = APIRouter(prefix="/analytics")


@router.get("/overview")
async def analytics_overview(db: DbSession, user: CurrentUser) -> dict:
    return {"data": await overview(db, user)}


@router.get("/audit-logs")
async def audit_logs(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    if not is_platform_admin(user):
        raise forbidden()
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
    all_rows = (await db.execute(stmt)).scalars().all()
    total = len(all_rows)
    rows = all_rows[(page - 1) * page_size : page * page_size]
    return {
        "data": [
            {
                "id": r.id,
                "actor_id": r.actor_id,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "metadata": r.metadata_json,
                "created_at": r.created_at,
            }
            for r in rows
        ],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }
