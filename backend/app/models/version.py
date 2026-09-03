from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import LifecycleStage
from app.models.model import _now, _uuid


class ModelVersion(Base):
    __tablename__ = "model_versions"
    __table_args__ = (UniqueConstraint("model_id", "version", name="uq_model_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    stage: Mapped[LifecycleStage] = mapped_column(
        String(20), default=LifecycleStage.DRAFT, nullable=False
    )
    approved: Mapped[bool] = mapped_column(default=False, nullable=False)

    artifact_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    training_data_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now, nullable=False)

    model: Mapped["MLModel"] = relationship("MLModel", back_populates="versions")  # noqa: F821
