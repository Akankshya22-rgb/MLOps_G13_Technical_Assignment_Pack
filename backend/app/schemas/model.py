from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.version import VersionRead


class ModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    owner: str = Field(..., min_length=1, max_length=200)
    framework: str = Field(..., min_length=1, max_length=100)
    algorithm: str | None = Field(default=None, max_length=100)
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class ModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    owner: str
    framework: str
    algorithm: str | None
    description: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class ModelWithVersions(ModelRead):
    versions: list[VersionRead] = Field(default_factory=list)
