from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import is_dept_admin, is_platform_admin, user_department_ids
from app.core.security import AuthUser
from app.models.entities import Assignment, Grievance, GrievanceCategory, GrievanceSLA
from app.models.enums import GrievanceStatus


async def overview(db: AsyncSession, user: AuthUser) -> dict:
    if not (is_platform_admin(user) or is_dept_admin(user)):
        from app.core.exceptions import forbidden

        raise forbidden("Analytics require administrator role")
    stmt = select(Grievance)
    dept_ids = None
    if is_dept_admin(user) and not is_platform_admin(user):
        dept_ids = await user_department_ids(db, user.id)
        stmt = stmt.where(Grievance.official_department_id.in_(dept_ids))
    grievances = (await db.execute(stmt)).scalars().all()
    total = len(grievances)
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    overdue = 0
    resolved = 0
    for g in grievances:
        st = g.status.value if hasattr(g.status, "value") else str(g.status)
        by_status[st] = by_status.get(st, 0) + 1
        if g.official_priority:
            pr = g.official_priority.value if hasattr(g.official_priority, "value") else str(g.official_priority)
            by_priority[pr] = by_priority.get(pr, 0) + 1
        if st in {GrievanceStatus.resolved.value, GrievanceStatus.closed.value}:
            resolved += 1
    sla_stmt = select(GrievanceSLA).join(Grievance, Grievance.id == GrievanceSLA.grievance_id)
    if dept_ids:
        sla_stmt = sla_stmt.where(Grievance.official_department_id.in_(dept_ids))
    sla_rows = (await db.execute(sla_stmt)).scalars().all()
    for sla in sla_rows:
        if sla.breached_resolution or sla.breached_first_response:
            overdue += 1
    dept_workload = []
    if is_platform_admin(user):
        result = await db.execute(
            select(Grievance.official_department_id, func.count())
            .where(Grievance.official_department_id.is_not(None))
            .group_by(Grievance.official_department_id)
        )
        for dept_id, count in result.all():
            dept_workload.append({"department_id": dept_id, "open_count": count, "overdue_count": 0})
    pending = sum(
        by_status.get(s, 0)
        for s in [
            GrievanceStatus.submitted.value,
            GrievanceStatus.needs_information.value,
            GrievanceStatus.under_review.value,
            GrievanceStatus.assigned.value,
            GrievanceStatus.in_progress.value,
        ]
    )
    in_progress = by_status.get(GrievanceStatus.in_progress.value, 0)
    sla_compliance_rate = None
    if sla_rows:
        ok = sum(1 for s in sla_rows if not (s.breached_resolution or s.breached_first_response))
        sla_compliance_rate = round(ok / len(sla_rows), 4)
    return {
        "total_grievances": total,
        "pending_grievances": pending,
        "in_progress_grievances": in_progress,
        "overdue_count": overdue,
        "resolved_grievances": resolved,
        "by_status": by_status,
        "by_priority": by_priority,
        "sla_compliance_rate": sla_compliance_rate,
        "avg_resolution_hours": None,
        "department_workload": dept_workload,
    }
