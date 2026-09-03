"""Business rules for deployment requests, retries and rollbacks."""

from app.domain.lifecycle import DEPLOYABLE_STAGES_BY_ENVIRONMENT
from app.errors import LifecycleError, ValidationError
from app.models.enums import DeploymentStatus
from app.models.version import ModelVersion

VALID_ENVIRONMENTS = {"staging", "production"}


def validate_environment(environment: str) -> None:
    if environment not in VALID_ENVIRONMENTS:
        raise ValidationError(
            f"Unsupported environment '{environment}'.",
            details={"valid_environments": sorted(VALID_ENVIRONMENTS)},
        )


def validate_version_deployable(version: ModelVersion, environment: str) -> None:
    """Enforce that only approved, sufficiently-promoted versions may be deployed.

    Production deployment additionally requires explicit approval, independent of
    stage, so an approval can never be bypassed by stage alone.
    """
    if not version.approved:
        raise LifecycleError(
            f"Model version '{version.version}' has not been approved and cannot be deployed.",
            details={"model_id": version.model_id, "version": version.version, "environment": environment},
        )

    allowed_stages = DEPLOYABLE_STAGES_BY_ENVIRONMENT.get(environment, set())
    if version.stage not in allowed_stages:
        raise LifecycleError(
            f"Model version '{version.version}' in stage '{version.stage.value if hasattr(version.stage, 'value') else version.stage}' "
            f"cannot be deployed to '{environment}'.",
            details={
                "model_id": version.model_id,
                "version": version.version,
                "stage": str(version.stage),
                "environment": environment,
            },
        )


def validate_retryable(status: DeploymentStatus) -> None:
    if status != DeploymentStatus.FAILED:
        raise LifecycleError(
            f"Deployment in status '{status.value if hasattr(status, 'value') else status}' cannot be retried; only FAILED deployments can be retried.",
            details={"status": str(status)},
        )


def validate_rollback_allowed(status: DeploymentStatus) -> None:
    if status != DeploymentStatus.SUCCEEDED:
        raise LifecycleError(
            f"Deployment in status '{status.value if hasattr(status, 'value') else status}' cannot be rolled back; only SUCCEEDED deployments can be rolled back.",
            details={"status": str(status)},
        )
