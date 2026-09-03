"""Model-version lifecycle state machine.

Stages progress DRAFT -> VALIDATED -> APPROVED -> STAGING -> PRODUCTION -> ARCHIVED.
A version can also be archived directly from APPROVED or STAGING (e.g. superseded
before ever reaching production), and PRODUCTION can fall back to STAGING when a
rollback demotes it.
"""

from app.errors import LifecycleError
from app.models.enums import LifecycleStage

ALLOWED_TRANSITIONS: dict[LifecycleStage, set[LifecycleStage]] = {
    LifecycleStage.DRAFT: {LifecycleStage.VALIDATED, LifecycleStage.ARCHIVED},
    LifecycleStage.VALIDATED: {LifecycleStage.APPROVED, LifecycleStage.ARCHIVED},
    LifecycleStage.APPROVED: {LifecycleStage.STAGING, LifecycleStage.ARCHIVED},
    LifecycleStage.STAGING: {LifecycleStage.PRODUCTION, LifecycleStage.APPROVED, LifecycleStage.ARCHIVED},
    LifecycleStage.PRODUCTION: {LifecycleStage.STAGING, LifecycleStage.ARCHIVED},
    LifecycleStage.ARCHIVED: set(),
}

# Stages a version must have reached before it may be deployed to a given environment.
DEPLOYABLE_STAGES_BY_ENVIRONMENT: dict[str, set[LifecycleStage]] = {
    "staging": {LifecycleStage.APPROVED, LifecycleStage.STAGING, LifecycleStage.PRODUCTION},
    "production": {LifecycleStage.APPROVED, LifecycleStage.STAGING, LifecycleStage.PRODUCTION},
}


def validate_transition(current: LifecycleStage, target: LifecycleStage) -> None:
    if target == current:
        return
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise LifecycleError(
            f"Cannot transition model version from '{current.value}' to '{target.value}'.",
            details={"current_stage": current.value, "target_stage": target.value},
        )


def stage_for_environment(environment: str) -> LifecycleStage:
    return LifecycleStage.PRODUCTION if environment == "production" else LifecycleStage.STAGING
