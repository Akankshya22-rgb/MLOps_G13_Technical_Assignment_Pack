from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.lifecycle import validate_transition
from app.errors import ConflictError, NotFoundError
from app.models.enums import LifecycleStage
from app.models.model import MLModel
from app.models.version import ModelVersion
from app.schemas.model import ModelCreate
from app.schemas.version import VersionCreate


def create_model(db: Session, payload: ModelCreate) -> MLModel:
    existing = db.execute(select(MLModel).where(MLModel.name == payload.name)).scalar_one_or_none()
    if existing is not None:
        raise ConflictError(f"A model named '{payload.name}' already exists.", details={"name": payload.name})

    model = MLModel(
        name=payload.name,
        owner=payload.owner,
        framework=payload.framework,
        algorithm=payload.algorithm,
        description=payload.description,
        tags=payload.tags,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def list_models(db: Session, search: str | None = None) -> list[MLModel]:
    stmt = select(MLModel).order_by(MLModel.created_at)
    models = list(db.execute(stmt).scalars().all())
    if search:
        needle = search.lower()
        models = [
            m
            for m in models
            if needle in m.name.lower()
            or needle in m.owner.lower()
            or needle in m.framework.lower()
            or any(needle in tag.lower() for tag in m.tags)
        ]
    return models


def get_model(db: Session, model_id: str) -> MLModel:
    model = db.get(MLModel, model_id)
    if model is None:
        raise NotFoundError(f"Model '{model_id}' was not found.", details={"model_id": model_id})
    return model


def create_version(db: Session, model_id: str, payload: VersionCreate) -> ModelVersion:
    model = get_model(db, model_id)

    existing = db.execute(
        select(ModelVersion).where(
            ModelVersion.model_id == model.id, ModelVersion.version == payload.version
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise ConflictError(
            f"Version '{payload.version}' already exists for model '{model_id}'.",
            details={"model_id": model_id, "version": payload.version},
        )

    version = ModelVersion(
        model_id=model.id,
        version=payload.version,
        artifact_uri=payload.artifact_uri,
        training_data_ref=payload.training_data_ref,
        metadata_json=payload.metadata,
        notes=payload.notes,
        stage=LifecycleStage.DRAFT,
        approved=False,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def list_versions(db: Session, model_id: str) -> list[ModelVersion]:
    get_model(db, model_id)
    stmt = (
        select(ModelVersion)
        .where(ModelVersion.model_id == model_id)
        .order_by(ModelVersion.created_at)
    )
    return list(db.execute(stmt).scalars().all())


def get_version(db: Session, model_id: str, version_id: str) -> ModelVersion:
    get_model(db, model_id)
    version = db.get(ModelVersion, version_id)
    if version is None or version.model_id != model_id:
        raise NotFoundError(
            f"Version '{version_id}' was not found for model '{model_id}'.",
            details={"model_id": model_id, "version_id": version_id},
        )
    return version


def approve_version(db: Session, model_id: str, version_id: str) -> ModelVersion:
    version = get_version(db, model_id, version_id)

    stage = LifecycleStage(version.stage)
    if stage == LifecycleStage.DRAFT:
        validate_transition(stage, LifecycleStage.VALIDATED)
        version.stage = LifecycleStage.VALIDATED
        stage = LifecycleStage.VALIDATED

    validate_transition(stage, LifecycleStage.APPROVED)
    version.stage = LifecycleStage.APPROVED
    version.approved = True

    db.commit()
    db.refresh(version)
    return version
