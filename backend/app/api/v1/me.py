from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.permissions import permissions_for
from app.models.entities import DepartmentOfficer, NotificationPreference
from app.schemas.common import DataResponse

router = APIRouter()


class ProfilePatch(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    locale: str | None = Field(None, pattern="^(en|te)$")


class NotificationPrefOut(BaseModel):
    in_app_enabled: bool
    email_enabled: bool
    sms_enabled: bool
    web_push_enabled: bool
    whatsapp_enabled: bool
    marketing_campaigns_enabled: bool
    emergency_alerts_enabled: bool
    locale: str


class NotificationPrefIn(NotificationPrefOut):
    pass


@router.get("/me")
async def get_me(db: DbSession, user: CurrentUser) -> dict:
    from app.models.entities import Profile

    profile = await db.get(Profile, user.id)
    dept_ids = (
        await db.execute(select(DepartmentOfficer.department_id).where(DepartmentOfficer.officer_id == user.id))
    ).scalars().all()
    pref = await db.get(NotificationPreference, user.id)
    return {
        "data": {
            "id": user.id,
            "email": user.email,
            "full_name": profile.full_name if profile else None,
            "phone": profile.phone if profile else None,
            "role": user.role.value,
            "permissions": permissions_for(user),
            "department_ids": list(dept_ids),
            "locale": pref.locale if pref else "en",
            "created_at": profile.created_at.isoformat().replace("+00:00", "Z") if profile else None,
            "updated_at": profile.updated_at.isoformat().replace("+00:00", "Z") if profile else None,
        }
    }


@router.patch("/me")
async def patch_me(db: DbSession, user: CurrentUser, body: ProfilePatch) -> dict:
    from app.models.entities import Profile

    profile = await db.get(Profile, user.id)
    if not profile:
        from app.core.exceptions import not_found

        raise not_found("Profile not found")
    if body.full_name is not None:
        profile.full_name = body.full_name
    if body.phone is not None:
        profile.phone = body.phone
    if body.locale is not None:
        from app.services.notifications import ensure_preferences

        pref = await ensure_preferences(db, user.id)
        pref.locale = body.locale
    return (await get_me(db, user))


@router.get("/me/notification-preferences")
async def get_notification_preferences(db: DbSession, user: CurrentUser) -> dict:
    from app.services.notifications import ensure_preferences

    pref = await ensure_preferences(db, user.id)
    return {"data": NotificationPrefOut.model_validate(pref, from_attributes=True).model_dump()}


@router.put("/me/notification-preferences")
async def put_notification_preferences(db: DbSession, user: CurrentUser, body: NotificationPrefIn) -> dict:
    from app.services.notifications import ensure_preferences

    pref = await ensure_preferences(db, user.id)
    for field in NotificationPrefIn.model_fields:
        setattr(pref, field, getattr(body, field))
    return {"data": NotificationPrefOut.model_validate(pref, from_attributes=True).model_dump()}
