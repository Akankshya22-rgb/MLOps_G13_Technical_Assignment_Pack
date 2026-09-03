import pytest

from app.domain.lifecycle import stage_for_environment, validate_transition
from app.errors import LifecycleError
from app.models.enums import LifecycleStage


@pytest.mark.parametrize(
    "current,target",
    [
        (LifecycleStage.DRAFT, LifecycleStage.VALIDATED),
        (LifecycleStage.VALIDATED, LifecycleStage.APPROVED),
        (LifecycleStage.APPROVED, LifecycleStage.STAGING),
        (LifecycleStage.STAGING, LifecycleStage.PRODUCTION),
        (LifecycleStage.PRODUCTION, LifecycleStage.ARCHIVED),
        (LifecycleStage.PRODUCTION, LifecycleStage.STAGING),
    ],
)
def test_allowed_transitions_succeed(current, target):
    validate_transition(current, target)  # should not raise


@pytest.mark.parametrize(
    "current,target",
    [
        (LifecycleStage.DRAFT, LifecycleStage.APPROVED),
        (LifecycleStage.DRAFT, LifecycleStage.PRODUCTION),
        (LifecycleStage.ARCHIVED, LifecycleStage.DRAFT),
        (LifecycleStage.APPROVED, LifecycleStage.PRODUCTION),
    ],
)
def test_disallowed_transitions_raise(current, target):
    with pytest.raises(LifecycleError):
        validate_transition(current, target)


def test_same_stage_transition_is_noop():
    validate_transition(LifecycleStage.STAGING, LifecycleStage.STAGING)


def test_stage_for_environment():
    assert stage_for_environment("production") == LifecycleStage.PRODUCTION
    assert stage_for_environment("staging") == LifecycleStage.STAGING
