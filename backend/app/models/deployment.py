from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import DeploymentStatus
from app.models.model import _now, _uuid


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id"), nullable=False)
    version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"), nullable=False)
    environment: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[DeploymentStatus] = mapped_column(
        String(20), default=DeploymentStatus.REQUESTED, nullable=False
    )
    idempotency_key: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    attempt_count: Mapped[int] = mapped_column(default=1, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    requested_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now, nullable=False)

    model: Mapped["MLModel"] = relationship("MLModel")  # noqa: F821
    version: Mapped["ModelVersion"] = relationship("ModelVersion")  # noqa: F821
    events: Mapped[list["DeploymentEvent"]] = relationship(  # noqa: F821
        "DeploymentEvent",
        back_populates="deployment",
        cascade="all, delete-orphan",
        order_by="DeploymentEvent.timestamp",
    )
