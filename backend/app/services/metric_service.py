from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.metric import Metric
from app.schemas.metric import MetricSummary, ModelMetricsResponse
from app.services.model_service import get_model


def compute_monitoring_status(metric: Metric) -> str:
    if metric.availability < 95 or metric.error_rate > 0.10:
        return "UNHEALTHY"
    if metric.drift_score > 0.30 or metric.error_rate > 0.05 or metric.quality_score < 0.80:
        return "DEGRADED"
    return "HEALTHY"


def get_model_metrics(
    db: Session,
    model_id: str,
    version: str | None = None,
    environment: str | None = None,
    limit: int = 200,
) -> ModelMetricsResponse:
    get_model(db, model_id)

    stmt = select(Metric).where(Metric.model_id == model_id)
    if version:
        stmt = stmt.where(Metric.version == version)
    if environment:
        stmt = stmt.where(Metric.environment == environment)
    stmt = stmt.order_by(Metric.timestamp.desc()).limit(limit)

    history = list(db.execute(stmt).scalars().all())
    history.reverse()  # chronological order for charting

    groups: dict[tuple[str, str], list[Metric]] = {}
    for m in history:
        groups.setdefault((m.version, m.environment), []).append(m)

    summaries = []
    for (v, env), rows in sorted(groups.items()):
        latest = rows[-1]
        summaries.append(
            MetricSummary(
                version=v,
                environment=env,
                latest=latest,
                monitoring_status=compute_monitoring_status(latest),
                last_successful_inference=latest.timestamp,
                sample_count=len(rows),
            )
        )

    return ModelMetricsResponse(model_id=model_id, summaries=summaries, history=history)
