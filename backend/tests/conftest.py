import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def registered_model(client):
    response = client.post(
        "/models",
        json={
            "name": "pump-failure-predictor",
            "owner": "Reliability AI Team",
            "framework": "scikit-learn",
            "algorithm": "random-forest",
            "description": "Predicts pump failure risk.",
            "tags": ["industrial", "predictive-maintenance"],
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def approved_version(client, registered_model):
    model_id = registered_model["id"]
    version_resp = client.post(
        f"/models/{model_id}/versions",
        json={
            "version": "1.0.0",
            "artifact_uri": "s3://models/pump/1.0.0",
            "training_data_ref": "s3://data/pump/2026-06",
        },
    )
    assert version_resp.status_code == 201
    version = version_resp.json()

    approve_resp = client.post(f"/models/{model_id}/versions/{version['id']}/approve")
    assert approve_resp.status_code == 200
    return approve_resp.json()
