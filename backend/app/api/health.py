import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db

logger = logging.getLogger("app.health")

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:  # pragma: no cover - defensive; exercised via integration failure paths
        logger.exception("Database health check failed")
        database_status = "unavailable"

    return {"status": "ok" if database_status == "connected" else "degraded", "database": database_status}
