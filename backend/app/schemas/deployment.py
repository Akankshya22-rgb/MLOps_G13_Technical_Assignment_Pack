from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DeploymentStatus


class DeploymentCreate(BaseModel):
    model_id: str
    version_id: str
    environment: str = Field(..., description="Target environment, e.g. 'staging' or 'production'")
    idempotency_key: str | None = Field(
        default=None,
        max_length=200,
        description="Optional client-supplied key; replaying the same key returns the original deployment.",
    )
    simulate_failure: bool = Field(
        default=False, description="Testing hook to force this deployment attempt to fail."
    )


class RetryRequest(BaseModel):
    simulate_failure: bool = Field(default=False, description="Testing hook to force the retry to fail.")


class DeploymentEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    deployment_id: str
    event_type: str
    status: str
    message: str | None
    timestamp: datetime


class DeploymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_id: str
    version_id: str
    environment: str
    status: DeploymentStatus
    idempotency_key: str | None
    attempt_count: int
    error_message: str | None
    requested_at: datetime
    updated_at: datetime


class DeploymentDetail(DeploymentRead):
    events: list[DeploymentEventRead] = Field(default_factory=list)
