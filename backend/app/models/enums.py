import enum


class LifecycleStage(str, enum.Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    ARCHIVED = "ARCHIVED"


class DeploymentStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    VALIDATING = "VALIDATING"
    DEPLOYING = "DEPLOYING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


ACTIVE_DEPLOYMENT_STATUSES = {
    DeploymentStatus.REQUESTED,
    DeploymentStatus.VALIDATING,
    DeploymentStatus.DEPLOYING,
}

TERMINAL_DEPLOYMENT_STATUSES = {
    DeploymentStatus.SUCCEEDED,
    DeploymentStatus.FAILED,
    DeploymentStatus.ROLLED_BACK,
}
