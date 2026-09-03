import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.metric import ModelMetricsResponse
from app.schemas.model import ModelCreate, ModelRead, ModelWithVersions
from app.schemas.version import VersionCreate, VersionRead
from app.services import metric_service, model_service

logger = logging.getLogger("app.models")

router = APIRouter(tags=["models"])


@router.post("/models", response_model=ModelRead, status_code=201)
def create_model(payload: ModelCreate, db: Session = Depends(get_db)) -> ModelRead:
    model = model_service.create_model(db, payload)
    logger.info("model_created id=%s name=%s", model.id, model.name)
    return model


@router.get("/models", response_model=list[ModelRead])
def list_models(search: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[ModelRead]:
    return model_service.list_models(db, search=search)


@router.get("/models/{model_id}", response_model=ModelWithVersions)
def get_model(model_id: str, db: Session = Depends(get_db)) -> ModelWithVersions:
    return model_service.get_model(db, model_id)


@router.post("/models/{model_id}/versions", response_model=VersionRead, status_code=201)
def create_version(model_id: str, payload: VersionCreate, db: Session = Depends(get_db)) -> VersionRead:
    version = model_service.create_version(db, model_id, payload)
    logger.info("version_created model_id=%s version=%s", model_id, version.version)
    return version


@router.get("/models/{model_id}/versions", response_model=list[VersionRead])
def list_versions(model_id: str, db: Session = Depends(get_db)) -> list[VersionRead]:
    return model_service.list_versions(db, model_id)


@router.get("/models/{model_id}/versions/{version_id}", response_model=VersionRead)
def get_version(model_id: str, version_id: str, db: Session = Depends(get_db)) -> VersionRead:
    return model_service.get_version(db, model_id, version_id)


@router.post("/models/{model_id}/versions/{version_id}/approve", response_model=VersionRead)
def approve_version(model_id: str, version_id: str, db: Session = Depends(get_db)) -> VersionRead:
    version = model_service.approve_version(db, model_id, version_id)
    logger.info("version_approved model_id=%s version=%s", model_id, version.version)
    return version


@router.get("/models/{model_id}/metrics", response_model=ModelMetricsResponse)
def get_model_metrics(
    model_id: str,
    version: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> ModelMetricsResponse:
    return metric_service.get_model_metrics(db, model_id, version=version, environment=environment, limit=limit)
