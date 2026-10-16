from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import forbidden, not_found, validation_error
from app.core.permissions import require_grievance_read
from app.core.security import AuthUser
from app.models.entities import Attachment
from app.services.grievances import get_grievance
from app.services.storage import build_object_path, get_storage_client, upload_expires_at


def validate_upload(content_type: str, size_bytes: int) -> None:
    settings = get_settings()
    if size_bytes <= 0 or size_bytes > settings.attachment_max_bytes:
        raise validation_error(
            f"File size must be between 1 and {settings.attachment_max_bytes} bytes",
            [{"field": "size_bytes", "message": "Out of allowed range"}],
        )
    ct = content_type.lower().split(";")[0].strip()
    if ct not in settings.allowed_attachment_types:
        raise validation_error(
            "File type not allowed",
            [{"field": "content_type", "message": f"Allowed: {', '.join(sorted(settings.allowed_attachment_types))}"}],
        )


async def create_upload_url(
    db: AsyncSession,
    user: AuthUser,
    grievance_id: UUID,
    *,
    file_name: str,
    content_type: str,
    size_bytes: int,
    attachment_role: str = "evidence",
) -> dict:
    validate_upload(content_type, size_bytes)
    g = await get_grievance(db, grievance_id)
    if g.citizen_id != user.id:
        from app.core.permissions import can_read_grievance, is_officer, is_platform_admin, is_dept_admin

        if not (
            is_officer(user)
            or is_dept_admin(user)
            or is_platform_admin(user)
        ) or not await can_read_grievance(db, user, g):
            raise forbidden("Not authorized to attach files to this grievance")
    attachment = Attachment(
        grievance_id=g.id,
        uploaded_by=user.id,
        file_name=file_name,
        content_type=content_type,
        size_bytes=size_bytes,
        storage_path="pending",
        attachment_role=attachment_role,
        upload_status="pending",
    )
    db.add(attachment)
    await db.flush()
    path = build_object_path(g.id, attachment.id, file_name)
    attachment.storage_path = path
    settings = get_settings()
    storage = get_storage_client()
    upload_url = await storage.create_signed_upload_url(path, content_type, settings.signed_url_ttl_seconds)
    expires = upload_expires_at(settings.signed_url_ttl_seconds)
    return {
        "attachment_id": attachment.id,
        "upload_url": upload_url,
        "storage_path": path,
        "expires_at": expires.isoformat().replace("+00:00", "Z"),
    }


async def complete_upload(db: AsyncSession, user: AuthUser, grievance_id: UUID, attachment_id: UUID) -> Attachment:
    g = await get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    att = await db.get(Attachment, attachment_id)
    if not att or att.grievance_id != g.id:
        raise not_found("Attachment not found")
    if att.uploaded_by != user.id and g.citizen_id != user.id:
        from app.core.permissions import can_read_grievance

        if not await can_read_grievance(db, user, g):
            raise forbidden()
    att.upload_status = "completed"
    return att


async def get_download_url(db: AsyncSession, user: AuthUser, grievance_id: UUID, attachment_id: UUID) -> dict:
    g = await get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    att = await db.get(Attachment, attachment_id)
    if not att or att.grievance_id != g.id or att.upload_status != "completed":
        raise not_found("Attachment not found")
    settings = get_settings()
    url = await get_storage_client().create_signed_download_url(att.storage_path, settings.signed_url_ttl_seconds)
    return {"download_url": url, "expires_at": upload_expires_at(settings.signed_url_ttl_seconds).isoformat()}


async def list_attachments(db: AsyncSession, user: AuthUser, grievance_id: UUID) -> list[Attachment]:
    g = await get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    rows = (
        await db.execute(select(Attachment).where(Attachment.grievance_id == g.id).order_by(Attachment.created_at.desc()))
    ).scalars().all()
    return list(rows)
