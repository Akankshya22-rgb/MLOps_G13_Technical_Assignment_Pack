from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.model import _now, _uuid


class DeploymentEvent(Base):
    __tablename__ = "deployment_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    deployment_id: Mapped[str] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(default=_now, nullable=False)

    deployment: Mapped["Deployment"] = relationship("Deployment", back_populates="events")  # noqa: F821
