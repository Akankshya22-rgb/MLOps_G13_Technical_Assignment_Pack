from collections import deque

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.deployment_rules import (
    validate_environment,
    validate_retryable,
    validate_rollback_allowed,
    validate_version_deployable,
)
from app.domain.lifecycle import ALLOWED_TRANSITIONS, stage_for_environment
from app.errors import ConflictError, LifecycleError, NotFoundError
from app.models.deployment import Deployment
from app.models.deployment_event import DeploymentEvent
from app.models.enums import ACTIVE_DEPLOYMENT_STATUSES, DeploymentStatus, LifecycleStage
from app.models.version import ModelVersion
from app.schemas.deployment import DeploymentCreate
from app.services.model_service import get_model, get_version


def _log_event(db: Session, deployment: Deployment, event_type: str, status: DeploymentStatus, message: str | None = None) -> None:
    db.add(
        DeploymentEvent(
            deployment_id=deployment.id,
            event_type=event_type,
            status=status.value,
            message=message,
        )
    )


def _stage_path(current: LifecycleStage, target: LifecycleStage) -> list[LifecycleStage] | None:
    """Breadth-first search over the allowed-transition graph for the shortest promotion path."""
    if current == target:
        return [current]

    queue: deque[list[LifecycleStage]] = deque([[current]])
    visited = {current}
    while queue:
        path = queue.popleft()
        node = path[-1]
        for nxt in ALLOWED_TRANSITIONS.get(node, set()):
            if nxt in visited:
                continue
            new_path = [*path, nxt]
            if nxt == target:
                return new_path
            visited.add(nxt)
            queue.append(new_path)
    return None


def _promote_version_stage(version: ModelVersion, environment: str) -> None:
    """Advance a version's lifecycle stage to reflect a successful deployment."""
    target = stage_for_environment(environment)
    current = LifecycleStage(version.stage)
    path = _stage_path(current, target)
    if path is None:
        raise LifecycleError(
            f"No valid lifecycle path from '{current.value}' to '{target.value}'.",
            details={"current_stage": current.value, "target_stage": target.value},
        )
    version.stage = target


def _run_pipeline(db: Session, deployment: Deployment, version: ModelVersion, simulate_failure: bool) -> None:
    """Synchronously simulate the deploy pipeline: VALIDATING -> DEPLOYING -> SUCCEEDED|FAILED.

    A real system would hand this off to an async worker/queue; here it runs inline so
    behaviour stays deterministic and easy to test (see docs/adr/0004-deployment-simulation.md).
    """
    deployment.status = DeploymentStatus.VALIDATING
    _log_event(db, deployment, "validation_started", deployment.status)

    deployment.status = DeploymentStatus.DEPLOYING
    _log_event(db, deployment, "deployment_started", deployment.status)

    if simulate_failure:
        deployment.status = DeploymentStatus.FAILED
        deployment.error_message = "Simulated deployment failure (requested via simulate_failure)."
        _log_event(db, deployment, "deployment_failed", deployment.status, deployment.error_message)
        return

    deployment.status = DeploymentStatus.SUCCEEDED
    deployment.error_message = None
    _promote_version_stage(version, deployment.environment)
    _log_event(db, deployment, "deployment_completed", deployment.status)


def create_deployment(db: Session, payload: DeploymentCreate) -> Deployment:
    validate_environment(payload.environment)
    get_model(db, payload.model_id)
    version = get_version(db, payload.model_id, payload.version_id)

    if payload.idempotency_key:
        existing = db.execute(
            select(Deployment).where(Deployment.idempotency_key == payload.idempotency_key)
        ).scalar_one_or_none()
        if existing is not None:
            return existing

    active = db.execute(
        select(Deployment).where(
            Deployment.model_id == payload.model_id,
            Deployment.version_id == payload.version_id,
            Deployment.environment == payload.environment,
            Deployment.status.in_([s.value for s in ACTIVE_DEPLOYMENT_STATUSES]),
        )
    ).scalar_one_or_none()
    if active is not None:
        raise ConflictError(
            "A deployment for this model version and environment is already in progress.",
            details={"existing_deployment_id": active.id, "status": str(active.status)},
        )

    validate_version_deployable(version, payload.environment)

    deployment = Deployment(
        model_id=payload.model_id,
        version_id=payload.version_id,
        environment=payload.environment,
        status=DeploymentStatus.REQUESTED,
        idempotency_key=payload.idempotency_key,
        attempt_count=1,
    )
    db.add(deployment)
    db.flush()
    _log_event(db, deployment, "deployment_requested", deployment.status)

    _run_pipeline(db, deployment, version, payload.simulate_failure)

    db.commit()
    db.refresh(deployment)
    return deployment


def list_deployments(
    db: Session, model_id: str | None = None, environment: str | None = None, status: str | None = None
) -> list[Deployment]:
    stmt = select(Deployment).order_by(Deployment.requested_at.desc())
    if model_id:
        stmt = stmt.where(Deployment.model_id == model_id)
    if environment:
        stmt = stmt.where(Deployment.environment == environment)
    if status:
        stmt = stmt.where(Deployment.status == status)
    return list(db.execute(stmt).scalars().all())


def get_deployment(db: Session, deployment_id: str) -> Deployment:
    deployment = db.get(Deployment, deployment_id)
    if deployment is None:
        raise NotFoundError(
            f"Deployment '{deployment_id}' was not found.", details={"deployment_id": deployment_id}
        )
    return deployment


def retry_deployment(db: Session, deployment_id: str, simulate_failure: bool = False) -> Deployment:
    deployment = get_deployment(db, deployment_id)
    validate_retryable(DeploymentStatus(deployment.status))

    version = get_version(db, deployment.model_id, deployment.version_id)
    validate_version_deployable(version, deployment.environment)

    deployment.attempt_count += 1
    deployment.status = DeploymentStatus.REQUESTED
    _log_event(db, deployment, "deployment_retry_requested", deployment.status)

    _run_pipeline(db, deployment, version, simulate_failure)

    db.commit()
    db.refresh(deployment)
    return deployment


def rollback_deployment(db: Session, deployment_id: str) -> Deployment:
    deployment = get_deployment(db, deployment_id)
    validate_rollback_allowed(DeploymentStatus(deployment.status))

    previous = db.execute(
        select(Deployment)
        .where(
            Deployment.model_id == deployment.model_id,
            Deployment.environment == deployment.environment,
            Deployment.status == DeploymentStatus.SUCCEEDED.value,
            Deployment.id != deployment.id,
            Deployment.requested_at < deployment.requested_at,
        )
        .order_by(Deployment.requested_at.desc())
    ).scalars().first()

    if previous is None:
        raise LifecycleError(
            "No prior successful deployment exists for this model and environment to roll back to.",
            details={"model_id": deployment.model_id, "environment": deployment.environment},
        )

    current_version = get_version(db, deployment.model_id, deployment.version_id)
    previous_version = get_version(db, previous.model_id, previous.version_id)

    deployment.status = DeploymentStatus.ROLLED_BACK
    _log_event(
        db,
        deployment,
        "deployment_rolled_back",
        deployment.status,
        message=f"Rolled back in favour of version '{previous_version.version}' (deployment {previous.id}).",
    )

    current_version.stage = LifecycleStage.STAGING
    previous_version.stage = stage_for_environment(deployment.environment)

    db.commit()
    db.refresh(deployment)
    return deployment
