from datetime import UTC, datetime

from app.services.metric_service import compute_monitoring_status


class FakeMetric:
    def __init__(self, availability, error_rate, drift_score, quality_score):
        self.availability = availability
        self.error_rate = error_rate
        self.drift_score = drift_score
        self.quality_score = quality_score
        self.timestamp = datetime.now(UTC)


def test_healthy_metric():
    metric = FakeMetric(availability=99.9, error_rate=0.01, drift_score=0.05, quality_score=0.95)
    assert compute_monitoring_status(metric) == "HEALTHY"


def test_degraded_on_drift():
    metric = FakeMetric(availability=99.9, error_rate=0.01, drift_score=0.35, quality_score=0.95)
    assert compute_monitoring_status(metric) == "DEGRADED"


def test_degraded_on_quality():
    metric = FakeMetric(availability=99.9, error_rate=0.01, drift_score=0.05, quality_score=0.5)
    assert compute_monitoring_status(metric) == "DEGRADED"


def test_unhealthy_on_low_availability():
    metric = FakeMetric(availability=90.0, error_rate=0.01, drift_score=0.05, quality_score=0.95)
    assert compute_monitoring_status(metric) == "UNHEALTHY"


def test_unhealthy_on_high_error_rate():
    metric = FakeMetric(availability=99.9, error_rate=0.2, drift_score=0.05, quality_score=0.95)
    assert compute_monitoring_status(metric) == "UNHEALTHY"
