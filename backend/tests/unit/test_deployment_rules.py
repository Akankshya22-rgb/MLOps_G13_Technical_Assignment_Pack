import pytest

from app.domain.deployment_rules import (
    validate_environment,
    validate_retryable,
    validate_rollback_allowed,
    validate_version_deployable,
)
from app.errors import LifecycleError, ValidationError
from app.models.enums import DeploymentStatus, LifecycleStage


class FakeVersion:
    def __init__(self, approved: bool, stage: LifecycleStage, version: str = "1.0.0", model_id: str = "m1"):
        self.approved = approved
        self.stage = stage
        self.version = version
        self.model_id = model_id


def test_validate_environment_rejects_unknown():
    with pytest.raises(ValidationError):
        validate_environment("canary")


def test_unapproved_version_blocked_from_production():
    version = FakeVersion(approved=False, stage=LifecycleStage.STAGING)
    with pytest.raises(LifecycleError):
        validate_version_deployable(version, "production")


def test_draft_version_blocked_even_if_approved_flag_set():
    version = FakeVersion(approved=True, stage=LifecycleStage.DRAFT)
    with pytest.raises(LifecycleError):
        validate_version_deployable(version, "staging")


def test_approved_version_deployable_to_staging_and_production():
    version = FakeVersion(approved=True, stage=LifecycleStage.APPROVED)
    validate_version_deployable(version, "staging")
    validate_version_deployable(version, "production")


def test_only_failed_deployments_are_retryable():
    validate_retryable(DeploymentStatus.FAILED)
    for status in (DeploymentStatus.SUCCEEDED, DeploymentStatus.REQUESTED, DeploymentStatus.ROLLED_BACK):
        with pytest.raises(LifecycleError):
            validate_retryable(status)


def test_only_succeeded_deployments_can_be_rolled_back():
    validate_rollback_allowed(DeploymentStatus.SUCCEEDED)
    for status in (DeploymentStatus.FAILED, DeploymentStatus.REQUESTED, DeploymentStatus.ROLLED_BACK):
        with pytest.raises(LifecycleError):
            validate_rollback_allowed(status)
