from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.exceptions import not_found
from app.models.entities import Notification

router = APIRouter(prefix="/notifications")


@router.get("")
async def list_notifications(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    stmt = select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())
    total = len((await db.execute(stmt)).scalars().all())
    rows = (
        await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return {
        "data": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "body": n.body,
                "grievance_id": n.grievance_id,
                "read_at": n.read_at,
                "created_at": n.created_at,
            }
            for n in rows
        ],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@router.post("/{notification_id}/read")
async def mark_read(db: DbSession, user: CurrentUser, notification_id: UUID) -> dict:
    from datetime import datetime, timezone

    n = await db.get(Notification, notification_id)
    if not n or n.user_id != user.id:
        raise not_found("Notification not found")
    n.read_at = datetime.now(timezone.utc)
    return {"data": {"id": n.id, "read_at": n.read_at}}
