#!/usr/bin/env python
"""Loads the sample data under data/ directly into the configured database.

This is a demo/dev convenience, not an API client: it writes rows straight to the
database (bypassing the deployment pipeline and lifecycle validation) so historical
metrics and deployment events can be pre-populated exactly as recorded in the sample
files, including states that the live pipeline would never produce.

Usage:
    docker compose exec backend python scripts/seed_data.py
    # or locally, with the backend's virtualenv active and DATABASE_URL exported:
    python scripts/seed_data.py
"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.database import SessionLocal, init_db  # noqa: E402
from app.models.deployment import Deployment  # noqa: E402
from app.models.deployment_event import DeploymentEvent  # noqa: E402
from app.models.enums import LifecycleStage  # noqa: E402
from app.models.metric import Metric  # noqa: E402
from app.models.model import MLModel  # noqa: E402
from app.models.version import ModelVersion  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_or_create_model(session, slug: str, *, owner="Unknown", framework="unknown") -> MLModel:
    model = session.query(MLModel).filter_by(name=slug).one_or_none()
    if model is None:
        model = MLModel(name=slug, owner=owner, framework=framework, tags=["seed-data"])
        session.add(model)
        session.flush()
        print(f"  created model '{slug}'")
    return model


def get_or_create_version(session, model: MLModel, version: str, *, stage: LifecycleStage, approved: bool, artifact_uri: str) -> ModelVersion:
    row = session.query(ModelVersion).filter_by(model_id=model.id, version=version).one_or_none()
    if row is None:
        row = ModelVersion(
            model_id=model.id,
            version=version,
            stage=stage,
            approved=approved,
            artifact_uri=artifact_uri,
        )
        session.add(row)
        session.flush()
        print(f"  created version {model.name}:{version} ({stage.value})")
    return row


def seed_registry(session) -> None:
    print("Seeding model registry...")
    registry = json.loads((DATA_DIR / "sample_model_registry.json").read_text())
    for entry in registry:
        model = get_or_create_model(session, entry["model_id"], owner=entry["owner"], framework=entry["framework"])
        for v in entry["versions"]:
            get_or_create_version(
                session,
                model,
                v["version"],
                stage=LifecycleStage(v["stage"]),
                approved=v["approved"],
                artifact_uri=v["artifact_uri"],
            )


def seed_metrics(session) -> None:
    print("Seeding monitoring metrics...")
    count = 0
    with (DATA_DIR / "sample_model_metrics.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
            model = get_or_create_model(session, row["model_id"])
            get_or_create_version(
                session,
                model,
                row["version"],
                stage=LifecycleStage.PRODUCTION,
                approved=True,
                artifact_uri=f"s3://models/{row['model_id']}/{row['version']}",
            )
            existing = (
                session.query(Metric)
                .filter_by(model_id=model.id, version=row["version"], environment=row["environment"], timestamp=parse_timestamp(row["timestamp"]))
                .one_or_none()
            )
            if existing is not None:
                continue
            session.add(
                Metric(
                    model_id=model.id,
                    version=row["version"],
                    environment=row["environment"],
                    timestamp=parse_timestamp(row["timestamp"]),
                    latency_ms=float(row["latency_ms"]),
                    throughput_rpm=float(row["throughput_rpm"]),
                    error_rate=float(row["error_rate"]),
                    quality_score=float(row["quality_score"]),
                    drift_score=float(row["drift_score"]),
                    availability=float(row["availability"]),
                )
            )
            count += 1
    print(f"  inserted {count} metric samples")


def seed_deployment_events(session) -> None:
    print("Seeding deployment history...")
    events = json.loads((DATA_DIR / "sample_deployment_events.json").read_text())
    for event in events:
        model = session.query(MLModel).filter_by(name=event["model_id"]).one_or_none()
        if model is None:
            print(f"  skipping event for unknown model '{event['model_id']}'")
            continue
        version = session.query(ModelVersion).filter_by(model_id=model.id, version=event["version"]).one_or_none()
        if version is None:
            print(f"  skipping event for unknown version '{event['model_id']}:{event['version']}'")
            continue

        timestamp = parse_timestamp(event["timestamp"])
        deployment = Deployment(
            model_id=model.id,
            version_id=version.id,
            environment=event["environment"],
            status=event["status"],
            attempt_count=1,
            requested_at=timestamp,
            updated_at=timestamp,
        )
        session.add(deployment)
        session.flush()
        session.add(
            DeploymentEvent(
                deployment_id=deployment.id,
                event_type=event["event"],
                status=event["status"],
                timestamp=timestamp,
            )
        )
    print(f"  inserted {len(events)} historical deployment(s)")


def main() -> None:
    init_db()
    session = SessionLocal()
    try:
        seed_registry(session)
        seed_metrics(session)
        seed_deployment_events(session)
        session.commit()
        print("Done.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
