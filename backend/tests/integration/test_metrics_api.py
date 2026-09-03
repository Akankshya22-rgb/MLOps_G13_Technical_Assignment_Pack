from datetime import UTC, datetime, timedelta

from sqlalchemy import insert

from app.models.metric import Metric

_BASE_TIME = datetime(2026, 7, 1, tzinfo=UTC)
_next_offset = iter(range(1000))


def _seed_metric(db_session, model_id, **overrides):
    values = {
        "model_id": model_id,
        "version": "1.0.0",
        "environment": "production",
        "timestamp": _BASE_TIME + timedelta(minutes=next(_next_offset)),
        "latency_ms": 90.0,
        "throughput_rpm": 1000.0,
        "error_rate": 0.01,
        "quality_score": 0.9,
        "drift_score": 0.05,
        "availability": 99.9,
    }
    values.update(overrides)
    db_session.execute(insert(Metric).values(**values))
    db_session.commit()


def test_metrics_endpoint_returns_summary_and_history(client, db_session, registered_model):
    """Acceptance scenario 5: Show monitoring data."""
    model_id = registered_model["id"]
    _seed_metric(db_session, model_id)
    _seed_metric(db_session, model_id, error_rate=0.2, availability=90.0)

    response = client.get(f"/models/{model_id}/metrics")
    assert response.status_code == 200
    body = response.json()

    assert len(body["history"]) == 2
    assert len(body["summaries"]) == 1
    summary = body["summaries"][0]
    assert summary["version"] == "1.0.0"
    assert summary["environment"] == "production"
    assert summary["monitoring_status"] == "UNHEALTHY"
    assert summary["sample_count"] == 2


def test_metrics_endpoint_filters_by_version_and_environment(client, db_session, registered_model):
    model_id = registered_model["id"]
    _seed_metric(db_session, model_id, version="1.0.0", environment="staging")
    _seed_metric(db_session, model_id, version="2.0.0", environment="production")

    response = client.get(f"/models/{model_id}/metrics", params={"version": "2.0.0", "environment": "production"})
    body = response.json()
    assert len(body["history"]) == 1
    assert body["history"][0]["version"] == "2.0.0"


def test_metrics_for_unknown_model_returns_404(client):
    response = client.get("/models/does-not-exist/metrics")
    assert response.status_code == 404
