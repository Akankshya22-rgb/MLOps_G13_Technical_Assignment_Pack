import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.deployment import DeploymentCreate, DeploymentDetail, DeploymentRead, RetryRequest
from app.services import deployment_service

logger = logging.getLogger("app.deployments")

router = APIRouter(tags=["deployments"])


@router.post("/deployments", response_model=DeploymentRead, status_code=201)
def create_deployment(payload: DeploymentCreate, db: Session = Depends(get_db)) -> DeploymentRead:
    deployment = deployment_service.create_deployment(db, payload)
    logger.info(
        "deployment_requested id=%s environment=%s status=%s",
        deployment.id,
        deployment.environment,
        deployment.status,
    )
    return deployment


@router.get("/deployments", response_model=list[DeploymentRead])
def list_deployments(
    model_id: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DeploymentRead]:
    return deployment_service.list_deployments(db, model_id=model_id, environment=environment, status=status)


@router.get("/deployments/{deployment_id}", response_model=DeploymentDetail)
def get_deployment(deployment_id: str, db: Session = Depends(get_db)) -> DeploymentDetail:
    return deployment_service.get_deployment(db, deployment_id)


@router.post("/deployments/{deployment_id}/retry", response_model=DeploymentRead)
def retry_deployment(deployment_id: str, payload: RetryRequest = RetryRequest(), db: Session = Depends(get_db)) -> DeploymentRead:
    deployment = deployment_service.retry_deployment(db, deployment_id, simulate_failure=payload.simulate_failure)
    logger.info("deployment_retried id=%s status=%s", deployment.id, deployment.status)
    return deployment


@router.post("/deployments/{deployment_id}/rollback", response_model=DeploymentRead)
def rollback_deployment(deployment_id: str, db: Session = Depends(get_db)) -> DeploymentRead:
    deployment = deployment_service.rollback_deployment(db, deployment_id)
    logger.info("deployment_rolled_back id=%s", deployment.id)
    return deployment
