from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.exceptions import forbidden, validation_error
from app.core.permissions import can_modify_grievance, require_grievance_read
from app.core.state_machine import normalize_status
from app.models.entities import Assignment, GrievanceEvent
from app.models.enums import GrievanceEventType, GrievanceStatus
from app.schemas.common import ListResponse, Meta
from app.schemas.grievance import (
    AnalyzeRequest,
    AssignmentRequest,
    EscalateRequest,
    FeedbackCreate,
    FollowUpResponsesBody,
    GrievanceCreate,
    GrievanceUpdateCitizen,
    GrievanceUpdateOfficer,
    SubmitAdditionalInfo,
    TransitionRequest,
)
from app.services import grievances as svc

router = APIRouter(prefix="/grievances")


@router.post("", status_code=201)
async def create_grievance(db: DbSession, user: CurrentUser, body: GrievanceCreate) -> dict:
    g = await svc.create_grievance(db, user, body)
    analysis = await svc.run_analysis(db, user, g.id, force=True)
    detail = svc.grievance_to_detail(g, analysis)
    return {"data": detail["grievance"]}


@router.get("")
async def list_grievances(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
    department_id: UUID | None = None,
    q: str | None = None,
) -> dict:
    rows, total = await svc.list_grievances(
        db, user, page=page, page_size=page_size, status=status, priority=priority, department_id=department_id, q=q
    )
    data = [
        {
            "id": g.id,
            "reference_id": g.reference_id,
            "status": normalize_status(GrievanceStatus(g.status)).value,
            "title": g.title,
            "description_preview": svc._preview(g.description),
            "official_priority": g.official_priority.value if g.official_priority else None,
            "official_department_id": g.official_department_id,
            "citizen_id": g.citizen_id,
            "created_at": g.created_at,
            "updated_at": g.updated_at,
            "urgency_score": float(g.urgency_score) if g.urgency_score is not None else None,
            "requires_human_review": g.requires_human_review,
        }
        for g in rows
    ]
    return {"data": data, "meta": {"page": page, "page_size": page_size, "total": total}}


@router.get("/{grievance_id}")
async def get_grievance(db: DbSession, user: CurrentUser, grievance_id: UUID) -> dict:
    g = await svc.get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    analysis = await svc.latest_analysis(db, g.id)
    detail = svc.grievance_to_detail(g, analysis)
    events = (
        await db.execute(
            select(GrievanceEvent).where(GrievanceEvent.grievance_id == g.id).order_by(GrievanceEvent.created_at)
        )
    ).scalars().all()
    detail["events"] = [
        {
            "id": e.id,
            "event_type": e.event_type.value if hasattr(e.event_type, "value") else e.event_type,
            "from_status": e.from_status.value if e.from_status else None,
            "to_status": e.to_status.value if e.to_status else None,
            "remark": e.remark if (e.metadata_json or {}).get("is_public") else None,
            "actor_id": e.actor_id,
            "created_at": e.created_at,
        }
        for e in events
    ]
    detail["assignments"] = [
        {
            "id": a.id,
            "department_id": a.department_id,
            "officer_id": a.officer_id,
            "assigned_at": a.assigned_at,
            "unassigned_at": a.unassigned_at,
        }
        for a in g.assignments
    ]
    return {"data": detail}


class GrievancePatch(GrievanceUpdateCitizen, GrievanceUpdateOfficer):
    pass


@router.patch("/{grievance_id}")
async def patch_grievance(db: DbSession, user: CurrentUser, grievance_id: UUID, body: GrievancePatch) -> dict:
    g = await svc.get_grievance(db, grievance_id)
    if not await can_modify_grievance(db, user, g):
        raise forbidden("Cannot modify this grievance")
    officer_fields = any(
        [
            body.official_category,
            body.official_department_id,
            body.official_priority,
            body.category_id,
            body.officer_remark,
        ]
    )
    if officer_fields:
        from app.core.permissions import can_transition

        if not can_transition(user):
            raise forbidden("Only authorized officials can set official fields")
        if body.official_category:
            g.official_category = body.official_category
        if body.official_department_id:
            g.official_department_id = body.official_department_id
        if body.official_priority:
            g.official_priority = body.official_priority
        if body.category_id:
            g.category_id = body.category_id
        if body.officer_remark:
            await svc.add_event(
                db,
                g,
                event_type=GrievanceEventType.remark,
                actor_id=user.id,
                remark=body.officer_remark,
                metadata={"is_public": False},
            )
    else:
        if g.citizen_id != user.id:
            raise forbidden("Citizens may only edit their own grievance content")
        if body.description:
            g.description = body.description
        if body.location_text:
            g.location_text = body.location_text
        if body.ward_or_locality:
            g.ward_or_locality = body.ward_or_locality
    analysis = await svc.latest_analysis(db, g.id)
    return {"data": svc.grievance_to_detail(g, analysis)["grievance"]}


@router.post("/{grievance_id}/submit-additional-info")
async def submit_additional_info(
    db: DbSession, user: CurrentUser, grievance_id: UUID, body: SubmitAdditionalInfo
) -> dict:
    g = await svc.submit_additional_info(db, user, grievance_id, body)
    analysis = await svc.run_analysis(db, user, g.id, force=True)
    return {"data": svc.grievance_to_detail(g, analysis)["grievance"]}


@router.post("/{grievance_id}/follow-up-responses")
async def follow_up_responses(
    db: DbSession, user: CurrentUser, grievance_id: UUID, body: FollowUpResponsesBody
) -> dict:
    wrapped = SubmitAdditionalInfo(responses=body.responses)
    return await submit_additional_info(db, user, grievance_id, wrapped)


@router.post("/{grievance_id}/transitions")
async def transition(db: DbSession, user: CurrentUser, grievance_id: UUID, body: TransitionRequest) -> dict:
    g = await svc.transition(db, user, grievance_id, body)
    analysis = await svc.latest_analysis(db, g.id)
    return {"data": svc.grievance_to_detail(g, analysis)["grievance"]}


@router.get("/{grievance_id}/track")
async def track(db: DbSession, user: CurrentUser, grievance_id: UUID) -> dict:
    data = await svc.build_track(db, user, grievance_id)
    return {"data": data}


@router.post("/{grievance_id}/analyze")
async def analyze(db: DbSession, user: CurrentUser, grievance_id: UUID, body: AnalyzeRequest | None = None) -> dict:
    force = body.force if body else False
    analysis = await svc.run_analysis(db, user, grievance_id, force=force)
    return {
        "data": {
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
    }


@router.post("/{grievance_id}/assignments", status_code=201)
async def assign(db: DbSession, user: CurrentUser, grievance_id: UUID, body: AssignmentRequest) -> dict:
    a = await svc.assign_grievance(db, user, grievance_id, body)
    return {
        "data": {
            "id": a.id,
            "department_id": a.department_id,
            "officer_id": a.officer_id,
            "assigned_at": a.assigned_at,
        }
    }


@router.post("/{grievance_id}/escalate")
async def escalate(db: DbSession, user: CurrentUser, grievance_id: UUID, body: EscalateRequest) -> dict:
    g = await svc.escalate(db, user, grievance_id, body.reason)
    analysis = await svc.latest_analysis(db, g.id)
    return {"data": svc.grievance_to_detail(g, analysis)["grievance"]}


@router.post("/{grievance_id}/feedback", status_code=201)
async def feedback(db: DbSession, user: CurrentUser, grievance_id: UUID, body: FeedbackCreate) -> dict:
    fb = await svc.submit_feedback(db, user, grievance_id, body)
    return {
        "data": {
            "id": fb.id,
            "grievance_id": fb.grievance_id,
            "rating": fb.rating,
            "satisfaction_score": fb.satisfaction_score,
            "comment": fb.comment,
            "created_at": fb.created_at,
        }
    }


@router.get("/{grievance_id}/feedback")
async def get_feedback(db: DbSession, user: CurrentUser, grievance_id: UUID) -> dict:
    g = await svc.get_grievance(db, grievance_id)
    await require_grievance_read(db, user, g)
    from app.models.entities import CitizenFeedback

    result = await db.execute(select(CitizenFeedback).where(CitizenFeedback.grievance_id == g.id))
    fb = result.scalar_one_or_none()
    if not fb:
        raise validation_error("No feedback for this grievance")
    return {"data": {"id": fb.id, "rating": fb.rating, "comment": fb.comment, "created_at": fb.created_at}}
