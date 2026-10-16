from __future__ import annotations

from fastapi import APIRouter, Query
from uuid import UUID

from app.api.deps import CurrentUser, DbSession
from app.core.exceptions import forbidden
from app.core.permissions import is_dept_admin, is_platform_admin, user_department_ids
from app.services import grievances as svc
from app.core.state_machine import normalize_status
from app.models.enums import GrievanceStatus

router = APIRouter(prefix="/dept")


@router.get("/grievances")
async def dept_queue(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
) -> dict:
    if not (is_dept_admin(user) or is_platform_admin(user)):
        raise forbidden("Department administrator access required")
    dept_ids = await user_department_ids(db, user.id)
    if is_dept_admin(user) and not dept_ids:
        return {"data": [], "meta": {"page": page, "page_size": page_size, "total": 0}}
    rows, total = await svc.list_grievances(
        db, user, page=page, page_size=page_size, status=status, priority=None, department_id=None, q=None
    )
    data = [
        {
            "id": g.id,
            "reference_id": g.reference_id,
            "status": normalize_status(GrievanceStatus(g.status)).value,
            "official_department_id": g.official_department_id,
            "urgency_score": float(g.urgency_score) if g.urgency_score is not None else None,
            "requires_human_review": g.requires_human_review,
            "created_at": g.created_at,
        }
        for g in rows
    ]
    return {"data": data, "meta": {"page": page, "page_size": page_size, "total": total}}
