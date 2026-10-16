from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.permissions import is_platform_admin
from app.core.exceptions import forbidden
from app.models.entities import Department, DepartmentOfficer

router = APIRouter(prefix="/departments")


class DepartmentCreate(BaseModel):
    name: str
    code: str
    description: str | None = None


class DepartmentPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class OfficersUpdate(BaseModel):
    officer_ids: list[UUID]


@router.get("")
async def list_departments(db: DbSession, user: CurrentUser) -> dict:
    stmt = select(Department).where(Department.is_active.is_(True))
    if not is_platform_admin(user):
        stmt = stmt.where(Department.is_active.is_(True))
    rows = (await db.execute(stmt.order_by(Department.name))).scalars().all()
    return {
        "data": [
            {"id": d.id, "name": d.name, "code": d.code, "description": d.description, "is_active": d.is_active}
            for d in rows
        ],
        "meta": {"page": 1, "page_size": len(rows), "total": len(rows)},
    }


@router.post("", status_code=201)
async def create_department(db: DbSession, user: CurrentUser, body: DepartmentCreate) -> dict:
    if not is_platform_admin(user):
        raise forbidden()
    d = Department(name=body.name, code=body.code, description=body.description)
    db.add(d)
    await db.flush()
    return {"data": {"id": d.id, "name": d.name, "code": d.code}}


@router.patch("/{department_id}")
async def patch_department(db: DbSession, user: CurrentUser, department_id: UUID, body: DepartmentPatch) -> dict:
    if not is_platform_admin(user):
        raise forbidden()
    d = await db.get(Department, department_id)
    if not d:
        from app.core.exceptions import not_found

        raise not_found()
    if body.name is not None:
        d.name = body.name
    if body.description is not None:
        d.description = body.description
    if body.is_active is not None:
        d.is_active = body.is_active
    return {"data": {"id": d.id, "name": d.name, "code": d.code, "is_active": d.is_active}}


@router.get("/{department_id}/officers")
async def get_officers(db: DbSession, user: CurrentUser, department_id: UUID) -> dict:
    if not is_platform_admin(user):
        raise forbidden()
    rows = (
        await db.execute(select(DepartmentOfficer.officer_id).where(DepartmentOfficer.department_id == department_id))
    ).scalars().all()
    return {"data": [{"officer_id": oid} for oid in rows]}


@router.put("/{department_id}/officers")
async def put_officers(db: DbSession, user: CurrentUser, department_id: UUID, body: OfficersUpdate) -> dict:
    if not is_platform_admin(user):
        raise forbidden()
    existing = (
        await db.execute(select(DepartmentOfficer).where(DepartmentOfficer.department_id == department_id))
    ).scalars().all()
    for row in existing:
        await db.delete(row)
    for oid in body.officer_ids:
        db.add(DepartmentOfficer(department_id=department_id, officer_id=oid))
    return {"data": {"officer_ids": body.officer_ids}}
