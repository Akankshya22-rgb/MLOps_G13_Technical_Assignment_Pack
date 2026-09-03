from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_id: str
    version: str
    environment: str
    timestamp: datetime
    latency_ms: float
    throughput_rpm: float
    error_rate: float
    quality_score: float
    drift_score: float
    availability: float


class MetricSummary(BaseModel):
    version: str
    environment: str
    latest: MetricRead | None
    monitoring_status: str
    last_successful_inference: datetime | None
    sample_count: int


class ModelMetricsResponse(BaseModel):
    model_id: str
    summaries: list[MetricSummary]
    history: list[MetricRead]
