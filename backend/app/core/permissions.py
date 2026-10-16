from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import forbidden
from app.core.security import AuthUser
from app.models.entities import Assignment, DepartmentOfficer, Grievance
from app.models.enums import GrievanceStatus, UserRole


def normalize_role(role: UserRole) -> UserRole:
    if role == UserRole.administrator:
        return UserRole.platform_administrator
    return role


def is_platform_admin(user: AuthUser) -> bool:
    r = normalize_role(user.role)
    return r == UserRole.platform_administrator


def is_dept_admin(user: AuthUser) -> bool:
    return normalize_role(user.role) == UserRole.department_administrator


def is_officer(user: AuthUser) -> bool:
    return normalize_role(user.role) == UserRole.officer


def is_citizen(user: AuthUser) -> bool:
    return normalize_role(user.role) == UserRole.citizen


def is_community_moderator(user: AuthUser) -> bool:
    return normalize_role(user.role) == UserRole.community_moderator


def permissions_for(user: AuthUser) -> list[str]:
    r = normalize_role(user.role)
    base = ["profile:read"]
    mapping = {
        UserRole.citizen: ["grievance:create", "grievance:read_own", "feedback:create"],
        UserRole.officer: ["grievance:read_assigned", "grievance:transition", "grievance:assign"],
        UserRole.department_administrator: [
            "grievance:read_dept",
            "grievance:transition",
            "grievance:assign",
            "analytics:dept",
        ],
        UserRole.platform_administrator: [
            "grievance:read_all",
            "grievance:transition",
            "grievance:assign",
            "department:manage",
            "analytics:all",
            "audit:read",
        ],
        UserRole.community_moderator: ["community:moderate"],
    }
    return base + mapping.get(r, [])


async def user_department_ids(db: AsyncSession, user_id: UUID) -> set[UUID]:
    result = await db.execute(
        select(DepartmentOfficer.department_id).where(DepartmentOfficer.officer_id == user_id)
    )
    return set(result.scalars().all())


async def can_read_grievance(db: AsyncSession, user: AuthUser, grievance: Grievance) -> bool:
    if is_community_moderator(user):
        return False
    if grievance.citizen_id == user.id:
        return True
    if is_platform_admin(user):
        return True
    if is_dept_admin(user) or is_officer(user):
        dept_ids = await user_department_ids(db, user.id)
        result = await db.execute(
            select(Assignment).where(
                Assignment.grievance_id == grievance.id,
                Assignment.is_current.is_(True),
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            return is_dept_admin(user) and grievance.official_department_id in dept_ids
        if assignment.officer_id == user.id:
            return True
        if assignment.department_id in dept_ids:
            return True
    return False


async def require_grievance_read(db: AsyncSession, user: AuthUser, grievance: Grievance) -> None:
    if not await can_read_grievance(db, user, grievance):
        raise forbidden("You do not have access to this grievance")


async def can_modify_grievance(db: AsyncSession, user: AuthUser, grievance: Grievance) -> bool:
    if is_platform_admin(user) or is_dept_admin(user):
        return await can_read_grievance(db, user, grievance)
    if is_officer(user):
        return await can_read_grievance(db, user, grievance)
    if is_citizen(user) and grievance.citizen_id == user.id:
        return grievance.status in {
            GrievanceStatus.submitted,
            GrievanceStatus.needs_information,
            GrievanceStatus.under_review,
            GrievanceStatus.in_review,
        }
    return False


def can_transition(user: AuthUser) -> bool:
    r = normalize_role(user.role)
    return r in {
        UserRole.officer,
        UserRole.department_administrator,
        UserRole.platform_administrator,
    }


def can_assign(user: AuthUser) -> bool:
    return can_transition(user)
