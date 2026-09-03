from datetime import datetime

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.model import _now, _uuid


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=_now, nullable=False)

    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    throughput_rpm: Mapped[float] = mapped_column(Float, nullable=False)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    drift_score: Mapped[float] = mapped_column(Float, nullable=False)
    availability: Mapped[float] = mapped_column(Float, nullable=False)
