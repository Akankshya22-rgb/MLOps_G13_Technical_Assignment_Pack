import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


class MLModel(Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    owner: Mapped[str] = mapped_column(String(200), nullable=False)
    framework: Mapped[str] = mapped_column(String(100), nullable=False)
    algorithm: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now, nullable=False)

    versions: Mapped[list["ModelVersion"]] = relationship(  # noqa: F821
        "ModelVersion", back_populates="model", cascade="all, delete-orphan", order_by="ModelVersion.created_at"
    )
