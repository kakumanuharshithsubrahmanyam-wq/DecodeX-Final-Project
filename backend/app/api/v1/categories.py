from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.entities import GrievanceCategory

router = APIRouter(prefix="/categories")


@router.get("")
async def list_categories(db: DbSession, user: CurrentUser) -> dict:
    result = await db.execute(
        select(GrievanceCategory).where(GrievanceCategory.is_active.is_(True)).order_by(GrievanceCategory.sort_order)
    )
    cats = result.scalars().all()
    by_parent: dict = {None: []}
    for c in cats:
        by_parent.setdefault(c.parent_id, []).append(c)

    def build(parent_id):
        nodes = []
        for c in by_parent.get(parent_id, []):
            nodes.append(
                {
                    "id": c.id,
                    "code": c.code,
                    "name": c.name,
                    "parent_id": c.parent_id,
                    "children": build(c.id),
                }
            )
        return nodes

    return {"data": build(None)}
