from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Grievance, GrievanceSLA, SLAPolicy
from app.models.enums import PriorityLevel


async def find_policy(
    db: AsyncSession,
    priority: PriorityLevel,
    category_id=None,
    department_id=None,
) -> SLAPolicy | None:
    stmt = (
        select(SLAPolicy)
        .where(SLAPolicy.is_active.is_(True), SLAPolicy.priority == priority)
        .order_by(SLAPolicy.category_id.desc().nullslast(), SLAPolicy.department_id.desc().nullslast())
    )
    result = await db.execute(stmt)
    policies = result.scalars().all()
    for p in policies:
        if category_id and p.category_id and p.category_id != category_id:
            continue
        if department_id and p.department_id and p.department_id != department_id:
            continue
        return p
    return policies[0] if policies else None


async def apply_sla_to_grievance(
    db: AsyncSession,
    grievance: Grievance,
    priority: PriorityLevel | None = None,
) -> GrievanceSLA:
    pri = priority or grievance.official_priority or PriorityLevel.medium
    if isinstance(pri, str):
        pri = PriorityLevel(pri)
    policy = await find_policy(db, pri, grievance.category_id, grievance.official_department_id)
    now = datetime.now(timezone.utc)
    first_hours = policy.first_response_hours if policy else 48
    resolution_hours = policy.resolution_hours if policy else 168
    result = await db.execute(select(GrievanceSLA).where(GrievanceSLA.grievance_id == grievance.id))
    sla = result.scalar_one_or_none()
    if not sla:
        sla = GrievanceSLA(grievance_id=grievance.id)
        db.add(sla)
    sla.policy_id = policy.id if policy else None
    sla.first_response_due_at = now + timedelta(hours=first_hours)
    sla.resolution_due_at = now + timedelta(hours=resolution_hours)
    grievance.resolution_due_at = sla.resolution_due_at
    return sla


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def evaluate_sla_breaches(sla: GrievanceSLA, now: datetime | None = None) -> list[str]:
    now = now or datetime.now(timezone.utc)
    warnings: list[str] = []
    if (
        sla.first_response_due_at
        and not sla.first_response_at
        and now > _as_utc(sla.first_response_due_at)
    ):
        sla.breached_first_response = True
        warnings.append("first_response_overdue")
    if sla.resolution_due_at and now > _as_utc(sla.resolution_due_at):
        sla.breached_resolution = True
        warnings.append("resolution_overdue")
    return warnings


def sla_to_dict(sla: GrievanceSLA | None) -> dict | None:
    if not sla:
        return None
    warnings = evaluate_sla_breaches(sla)
    return {
        "first_response_due_at": sla.first_response_due_at.isoformat().replace("+00:00", "Z")
        if sla.first_response_due_at
        else None,
        "resolution_due_at": sla.resolution_due_at.isoformat().replace("+00:00", "Z")
        if sla.resolution_due_at
        else None,
        "first_response_at": sla.first_response_at.isoformat().replace("+00:00", "Z")
        if sla.first_response_at
        else None,
        "breached": sla.breached_first_response or sla.breached_resolution,
        "warnings": warnings,
    }
