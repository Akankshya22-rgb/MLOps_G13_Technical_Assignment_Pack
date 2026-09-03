from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LifecycleStage


class VersionCreate(BaseModel):
    version: str = Field(..., min_length=1, max_length=50, description="Semantic version, e.g. 1.0.0")
    artifact_uri: str = Field(..., min_length=1, max_length=500)
    training_data_ref: str | None = Field(default=None, max_length=500)
    metadata: dict = Field(default_factory=dict)
    notes: str | None = None


class VersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    model_id: str
    version: str
    stage: LifecycleStage
    approved: bool
    artifact_uri: str
    training_data_ref: str | None
    metadata_json: dict = Field(serialization_alias="metadata")
    notes: str | None
    created_at: datetime
    updated_at: datetime
