from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.rules_engine import analyze_complaint
from app.core.exceptions import conflict, forbidden, not_found, validation_error
from app.core.permissions import (
    can_assign,
    can_read_grievance,
    can_transition,
    is_citizen,
    is_platform_admin,
    require_grievance_read,
    user_department_ids,
)
from app.core.security import AuthUser
from app.core.state_machine import normalize_status, validate_transition
from app.models.entities import (
    AIAnalysis,
    Assignment,
    CitizenFeedback,
    Department,
    Grievance,
    GrievanceCategory,
    GrievanceEvent,
)
from app.models.enums import AISource, GrievanceEventType, GrievanceStatus, PriorityLevel
from app.services.audit import log_action
from app.services.notifications import notify_user
from app.services.reference import generate_reference_id
from app.services.sla import apply_sla_to_grievance, evaluate_sla_breaches, sla_to_dict


def _preview(text: str, n: int = 160) -> str:
    t = text.strip()
    return t if len(t) <= n else t[: n - 3] + "..."


def _public_remark(event: GrievanceEvent) -> bool:
    meta = event.metadata_json or {}
    if meta.get("is_public") is False:
        return False
    if event.event_type == GrievanceEventType.remark and event.remark:
        return meta.get("is_public", False)
    return True


async def get_grievance(db: AsyncSession, grievance_id: UUID) -> Grievance:
    result = await db.execute(
        select(Grievance)
        .where(Grievance.id == grievance_id)
        .options(selectinload(Grievance.sla), selectinload(Grievance.assignments))
    )
    g = result.scalar_one_or_none()
    if not g:
        raise not_found("Grievance not found")
    return g


async def latest_analysis(db: AsyncSession, grievance_id: UUID) -> AIAnalysis | None:
    result = await db.execute(
        select(AIAnalysis)
        .where(AIAnalysis.grievance_id == grievance_id)
        .order_by(AIAnalysis.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def add_event(
    db: AsyncSession,
    grievance: Grievance,
    *,
    event_type: GrievanceEventType,
    actor_id: UUID | None,
    from_status: GrievanceStatus | None = None,
    to_status: GrievanceStatus | None = None,
    remark: str | None = None,
    metadata: dict | None = None,
) -> GrievanceEvent:
    ev = GrievanceEvent(
        grievance_id=grievance.id,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        remark=remark,
        metadata_json=metadata or {},
        actor_id=actor_id,
    )
    db.add(ev)
    return ev


async def create_grievance(db: AsyncSession, user: AuthUser, data) -> Grievance:
    if not is_citizen(user):
        raise forbidden("Only citizens can create grievances in MVP")
    ref = await generate_reference_id(db)
    g = Grievance(
        reference_id=ref,
        citizen_id=user.id,
        title=data.title,
        description=data.description,
        location_text=data.location_text,
        latitude=data.latitude,
        longitude=data.longitude,
        category_id=data.category_id,
        subcategory_id=data.subcategory_id,
        ward_or_locality=data.ward_or_locality,
        intake_channel=data.intake_channel,
        status=GrievanceStatus.submitted,
    )
    db.add(g)
    await db.flush()
    await add_event(
        db,
        g,
        event_type=GrievanceEventType.status_change,
        actor_id=user.id,
        from_status=None,
        to_status=GrievanceStatus.submitted,
        metadata={"is_public": True, "public_message": "Your grievance was submitted."},
    )
    await apply_sla_to_grievance(db, g, PriorityLevel.medium)
    await notify_user(
        db,
        user_id=user.id,
        type_="grievance_submitted",
        title="Grievance submitted",
        body=f"Reference {ref} registered successfully.",
        grievance_id=g.id,
        dedupe_key=f"submit:{g.id}",
    )
    return g


async def list_grievances(
    db: AsyncSession,
    user: AuthUser,
    *,
    page: int,
    page_size: int,
    status: str | None,
    priority: str | None,
    department_id: UUID | None,
    q: str | None,
) -> tuple[list[Grievance], int]:
    stmt = select(Grievance)
    if is_citizen(user):
        stmt = stmt.where(Grievance.citizen_id == user.id)
    elif is_platform_admin(user):
        pass
    else:
        dept_ids = await user_department_ids(db, user.id)
        stmt = stmt.join(Assignment, Assignment.grievance_id == Grievance.id, isouter=True).where(
            or_(
                Assignment.is_current.is_(True) & Assignment.department_id.in_(dept_ids),
                Assignment.is_current.is_(True) & (Assignment.officer_id == user.id),
                Grievance.official_department_id.in_(dept_ids),
            )
        )
    if status:
        stmt = stmt.where(Grievance.status == status)
    if priority:
        stmt = stmt.where(Grievance.official_priority == priority)
    if department_id:
        stmt = stmt.where(Grievance.official_department_id == department_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Grievance.reference_id.ilike(like), Grievance.description.ilike(like)))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(Grievance.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(stmt)).scalars().unique().all()
    return list(rows), total


async def run_analysis(db: AsyncSession, user: AuthUser, grievance_id: UUID, force: bool = False) -> AIAnalysis:
    g = await get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    existing = await latest_analysis(db, g.id)
    if existing and not force:
        created = existing.created_at
        if created and (datetime.now(timezone.utc) - created).total_seconds() < 60:
            return existing
    result = analyze_complaint(g.description, g.location_text, g.ward_or_locality)
    dept_id = None
    if result.suggested_department_code:
        dep = await db.execute(select(Department).where(Department.code == result.suggested_department_code))
        department = dep.scalar_one_or_none()
        dept_id = department.id if department else None
    version = (existing.version + 1) if existing else 1
    if result.missing_fields and normalize_status(GrievanceStatus(g.status)) == GrievanceStatus.submitted:
        g.status = GrievanceStatus.needs_information
        await add_event(
            db,
            g,
            event_type=GrievanceEventType.status_change,
            actor_id=None,
            from_status=GrievanceStatus.submitted,
            to_status=GrievanceStatus.needs_information,
            metadata={"is_public": True, "public_message": "Additional information is required."},
        )
        await notify_user(
            db,
            user_id=g.citizen_id,
            type_="needs_information",
            title="More information needed",
            body=f"Please provide details for {g.reference_id}.",
            grievance_id=g.id,
            dedupe_key=f"needs_info:{g.id}:{version}",
        )
    analysis = AIAnalysis(
        grievance_id=g.id,
        version=version,
        source=AISource.rules,
        summary=result.summary,
        extracted_entities=result.extracted_entities,
        suggested_category=result.suggested_category_code,
        suggested_department_id=dept_id,
        urgency_score=float(result.urgency_score),
        urgency_label=result.urgency_label,
        confidence=float(result.confidence),
        requires_human_review=result.requires_human_review,
        explanation=result.explanation,
        follow_up_questions=result.follow_up_questions,
    )
    g.urgency_score = float(result.urgency_score)
    g.requires_human_review = result.requires_human_review
    db.add(analysis)
    await add_event(db, g, event_type=GrievanceEventType.analysis, actor_id=user.id, metadata={"version": version})
    await apply_sla_to_grievance(db, g, result.urgency_label)
    return analysis


async def submit_additional_info(db: AsyncSession, user: AuthUser, grievance_id: UUID, body) -> Grievance:
    g = await get_grievance(db, grievance_id)
    if g.citizen_id != user.id:
        raise forbidden("Only the owner can submit additional information")
    if normalize_status(GrievanceStatus(g.status)) != GrievanceStatus.needs_information:
        raise validation_error("Grievance is not awaiting additional information")
    if body.description:
        g.description = f"{g.description}\n\nAdditional info: {body.description}"
    if body.location_text:
        g.location_text = body.location_text
    if body.responses:
        answers = "; ".join(f"{r.question_id}: {r.answer}" for r in body.responses)
        g.description = f"{g.description}\n\nFollow-up answers: {answers}"
    prev = g.status
    g.status = GrievanceStatus.under_review
    await add_event(
        db,
        g,
        event_type=GrievanceEventType.status_change,
        actor_id=user.id,
        from_status=prev,
        to_status=GrievanceStatus.under_review,
        metadata={"is_public": True, "public_message": "Additional information received."},
    )
    return g


async def transition(db: AsyncSession, user: AuthUser, grievance_id: UUID, body) -> Grievance:
    if not can_transition(user):
        raise forbidden("Insufficient permissions for status transition")
    g = await get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    current = GrievanceStatus(g.status)
    target = GrievanceStatus(body.to_status)
    validate_transition(current, target)
    prev = g.status
    g.status = normalize_status(target)
    if target == GrievanceStatus.resolved:
        g.resolved_at = datetime.now(timezone.utc)
    await add_event(
        db,
        g,
        event_type=GrievanceEventType.status_change,
        actor_id=user.id,
        from_status=prev,
        to_status=g.status,
        remark=body.remark,
        metadata={
            "is_public": True,
            "public_message": f"Status updated to {g.status.value.replace('_', ' ')}.",
        },
    )
    if body.remark:
        await add_event(
            db,
            g,
            event_type=GrievanceEventType.remark,
            actor_id=user.id,
            remark=body.remark,
            metadata={"is_public": False},
        )
    if g.sla and g.sla.first_response_at is None and target in {
        GrievanceStatus.under_review,
        GrievanceStatus.assigned,
        GrievanceStatus.in_progress,
    }:
        g.sla.first_response_at = datetime.now(timezone.utc)
    evaluate_sla_breaches(g.sla)
    await notify_user(
        db,
        user_id=g.citizen_id,
        type_="status_change",
        title="Grievance status updated",
        body=f"{g.reference_id} is now {g.status.value}.",
        grievance_id=g.id,
        dedupe_key=f"status:{g.id}:{g.status.value}",
    )
    await log_action(
        db,
        actor_id=user.id,
        action="grievance.transition",
        resource_type="grievance",
        resource_id=g.id,
        metadata={"to_status": g.status.value},
    )
    return g


async def assign_grievance(db: AsyncSession, user: AuthUser, grievance_id: UUID, body) -> Assignment:
    if not can_assign(user):
        raise forbidden("Insufficient permissions to assign")
    g = await get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    for a in g.assignments:
        if a.is_current:
            a.is_current = False
            a.unassigned_at = datetime.now(timezone.utc)
    assignment = Assignment(
        grievance_id=g.id,
        department_id=body.department_id,
        officer_id=body.officer_id,
        assigned_by=user.id,
        is_current=True,
    )
    db.add(assignment)
    g.official_department_id = body.department_id
    if normalize_status(GrievanceStatus(g.status)) in {
        GrievanceStatus.submitted,
        GrievanceStatus.under_review,
        GrievanceStatus.needs_information,
    }:
        validate_transition(GrievanceStatus(g.status), GrievanceStatus.assigned)
        prev = g.status
        g.status = GrievanceStatus.assigned
        await add_event(
            db,
            g,
            event_type=GrievanceEventType.status_change,
            actor_id=user.id,
            from_status=prev,
            to_status=GrievanceStatus.assigned,
            metadata={"is_public": True, "public_message": "Assigned to department."},
        )
    await add_event(db, g, event_type=GrievanceEventType.assignment, actor_id=user.id)
    await notify_user(
        db,
        user_id=g.citizen_id,
        type_="assigned",
        title="Grievance assigned",
        body=f"{g.reference_id} assigned to a department.",
        grievance_id=g.id,
        dedupe_key=f"assign:{g.id}:{assignment.id}",
    )
    return assignment


async def escalate(db: AsyncSession, user: AuthUser, grievance_id: UUID, reason: str) -> Grievance:
    body = type("T", (), {"to_status": GrievanceStatus.escalated, "remark": reason})()
    g = await get_grievance(db, grievance_id)
    try:
        validate_transition(GrievanceStatus(g.status), GrievanceStatus.escalated)
    except Exception:
        g.status = GrievanceStatus.escalated
        await add_event(
            db,
            g,
            event_type=GrievanceEventType.status_change,
            actor_id=user.id,
            to_status=GrievanceStatus.escalated,
            remark=reason,
            metadata={"is_public": True, "public_message": "Case escalated for priority review."},
        )
        return g
    return await transition(db, user, grievance_id, body)


async def submit_feedback(db: AsyncSession, user: AuthUser, grievance_id: UUID, data) -> CitizenFeedback:
    g = await get_grievance(db, grievance_id)
    if g.citizen_id != user.id:
        raise forbidden("Only the grievance owner can submit feedback")
    if normalize_status(GrievanceStatus(g.status)) not in {GrievanceStatus.resolved, GrievanceStatus.closed}:
        raise validation_error("Feedback allowed only after resolution")
    existing = await db.execute(
        select(CitizenFeedback).where(
            CitizenFeedback.grievance_id == g.id,
            CitizenFeedback.citizen_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise conflict("Feedback already submitted for this grievance")
    fb = CitizenFeedback(
        grievance_id=g.id,
        citizen_id=user.id,
        rating=data.rating,
        satisfaction_score=data.satisfaction_score,
        comment=data.comment,
        improvement_suggestion=data.improvement_suggestion,
    )
    db.add(fb)
    await add_event(db, g, event_type=GrievanceEventType.feedback, actor_id=user.id)
    return fb


async def build_track(db: AsyncSession, user: AuthUser, grievance_id: UUID) -> dict:
    g = await get_grievance(db, grievance_id)
    if g.citizen_id != user.id and not await can_read_grievance(db, user, g):
        raise forbidden()
    events = (
        await db.execute(
            select(GrievanceEvent)
            .where(GrievanceEvent.grievance_id == g.id)
            .order_by(GrievanceEvent.created_at.asc())
        )
    ).scalars().all()
    timeline = []
    for ev in events:
        if ev.event_type != GrievanceEventType.status_change and not _public_remark(ev):
            continue
        meta = ev.metadata_json or {}
        label = meta.get("public_message") or (ev.to_status.value if ev.to_status else ev.event_type.value)
        timeline.append(
            {
                "status": ev.to_status.value if ev.to_status else g.status.value,
                "label": label,
                "occurred_at": ev.created_at.isoformat().replace("+00:00", "Z"),
                "public_message": meta.get("public_message"),
            }
        )
    dept = None
    if g.official_department_id:
        d = await db.get(Department, g.official_department_id)
        if d:
            dept = {"id": str(d.id), "name": d.name}
    sla = sla_to_dict(g.sla)
    return {
        "reference_id": g.reference_id,
        "status": normalize_status(GrievanceStatus(g.status)).value,
        "timeline": timeline,
        "current_department": dept,
        "sla": sla,
        "resolution_summary": None,
    }


def grievance_to_detail(g: Grievance, analysis: AIAnalysis | None) -> dict:
    sla = g.sla
    sla_summary = None
    if sla:
        evaluate_sla_breaches(sla)
        sla_summary = {
            "first_response_due_at": sla.first_response_due_at,
            "resolution_due_at": sla.resolution_due_at,
            "breached": sla.breached_first_response or sla.breached_resolution,
            "warnings": evaluate_sla_breaches(sla),
        }
    latest = None
    if analysis:
        latest = {
            "id": analysis.id,
            "grievance_id": analysis.grievance_id,
            "version": analysis.version,
            "source": analysis.source.value if hasattr(analysis.source, "value") else analysis.source,
            "summary": analysis.summary,
            "extracted_entities": analysis.extracted_entities,
            "suggested_category": analysis.suggested_category,
            "suggested_department_id": analysis.suggested_department_id,
            "urgency_score": float(analysis.urgency_score),
            "urgency_label": analysis.urgency_label.value
            if hasattr(analysis.urgency_label, "value")
            else analysis.urgency_label,
            "confidence": float(analysis.confidence),
            "requires_human_review": analysis.requires_human_review,
            "explanation": analysis.explanation,
            "follow_up_questions": analysis.follow_up_questions,
            "created_at": analysis.created_at,
        }
    return {
        "grievance": {
            "id": g.id,
            "reference_id": g.reference_id,
            "status": normalize_status(GrievanceStatus(g.status)).value,
            "title": g.title,
            "description": g.description,
            "location_text": g.location_text,
            "latitude": g.latitude,
            "longitude": g.longitude,
            "citizen_id": g.citizen_id,
            "category_id": g.category_id,
            "official_category": g.official_category,
            "official_department_id": g.official_department_id,
            "official_priority": g.official_priority.value if g.official_priority else None,
            "urgency_score": float(g.urgency_score) if g.urgency_score is not None else None,
            "requires_human_review": g.requires_human_review,
            "created_at": g.created_at,
            "updated_at": g.updated_at,
            "sla": sla_summary,
            "latest_analysis": latest,
        },
        "events": [],
        "assignments": [],
        "attachments": [],
        "latest_analysis": latest,
    }
