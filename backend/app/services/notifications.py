from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Notification, NotificationPreference
from app.models.enums import NotificationChannel


async def ensure_preferences(db: AsyncSession, user_id: UUID) -> NotificationPreference:
    pref = await db.get(NotificationPreference, user_id)
    if not pref:
        pref = NotificationPreference(user_id=user_id, in_app_enabled=True, emergency_alerts_enabled=True)
        db.add(pref)
    return pref


async def notify_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    type_: str,
    title: str,
    body: str,
    grievance_id: UUID | None = None,
    dedupe_key: str | None = None,
) -> Notification | None:
    pref = await ensure_preferences(db, user_id)
    if pref.in_app_enabled is False:
        return None
    if dedupe_key:
        existing = await db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.dedupe_key == dedupe_key,
            )
        )
        if existing.scalar_one_or_none():
            return None
    notification = Notification(
        user_id=user_id,
        type=type_,
        title=title,
        body=body,
        grievance_id=grievance_id,
        channel=NotificationChannel.in_app,
        dedupe_key=dedupe_key,
    )
    db.add(notification)
    return notification
