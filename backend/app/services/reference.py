from __future__ import annotations

import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.entities import Grievance


async def generate_reference_id(db: AsyncSession) -> str:
    settings = get_settings()
    year = datetime.now(timezone.utc).year
    prefix = settings.grievance_ref_prefix
    for _ in range(10):
        suffix = secrets.token_hex(3).upper()[:6]
        ref = f"{prefix}-{year}-{suffix}"
        exists = await db.execute(select(Grievance.id).where(Grievance.reference_id == ref))
        if exists.scalar_one_or_none() is None:
            return ref
    raise RuntimeError("Unable to generate unique reference id")
