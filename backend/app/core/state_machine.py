from __future__ import annotations

from app.core.exceptions import conflict
from app.models.enums import GrievanceStatus

# Normalize legacy status
def normalize_status(status: GrievanceStatus) -> GrievanceStatus:
    if status == GrievanceStatus.in_review:
        return GrievanceStatus.under_review
    return status


ALLOWED_TRANSITIONS: dict[GrievanceStatus, set[GrievanceStatus]] = {
    GrievanceStatus.submitted: {
        GrievanceStatus.needs_information,
        GrievanceStatus.under_review,
        GrievanceStatus.assigned,
    },
    GrievanceStatus.needs_information: {
        GrievanceStatus.under_review,
        GrievanceStatus.submitted,
        GrievanceStatus.assigned,
    },
    GrievanceStatus.under_review: {
        GrievanceStatus.needs_information,
        GrievanceStatus.assigned,
        GrievanceStatus.escalated,
    },
    GrievanceStatus.assigned: {
        GrievanceStatus.in_progress,
        GrievanceStatus.needs_information,
        GrievanceStatus.escalated,
    },
    GrievanceStatus.in_progress: {
        GrievanceStatus.resolved,
        GrievanceStatus.needs_information,
        GrievanceStatus.escalated,
    },
    GrievanceStatus.resolved: {
        GrievanceStatus.closed,
        GrievanceStatus.reopened,
    },
    GrievanceStatus.closed: {GrievanceStatus.reopened},
    GrievanceStatus.reopened: {
        GrievanceStatus.under_review,
        GrievanceStatus.assigned,
        GrievanceStatus.in_progress,
    },
    GrievanceStatus.escalated: {
        GrievanceStatus.assigned,
        GrievanceStatus.in_progress,
        GrievanceStatus.resolved,
    },
}


def validate_transition(current: GrievanceStatus, target: GrievanceStatus) -> None:
    current = normalize_status(current)
    target = normalize_status(target)
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise conflict(f"Transition from {current.value} to {target.value} is not allowed")
