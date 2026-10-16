import pytest

from app.core.exceptions import AppError
from app.core.state_machine import validate_transition
from app.models.enums import GrievanceStatus


def test_valid_transition_submitted_to_under_review():
    validate_transition(GrievanceStatus.submitted, GrievanceStatus.under_review)


def test_invalid_transition_closed_to_in_progress():
    with pytest.raises(AppError) as exc:
        validate_transition(GrievanceStatus.closed, GrievanceStatus.in_progress)
    assert exc.value.code == "CONFLICT"
