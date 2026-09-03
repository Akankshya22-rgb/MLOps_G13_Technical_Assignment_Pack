def test_register_model_and_two_versions(client):
    """Acceptance scenario 1: Register a model and two versions."""
    model_resp = client.post(
        "/models",
        json={
            "name": "compressor-anomaly-detector",
            "owner": "Condition Monitoring Team",
            "framework": "pytorch",
            "tags": ["industrial"],
        },
    )
    assert model_resp.status_code == 201
    model_id = model_resp.json()["id"]

    v1 = client.post(
        f"/models/{model_id}/versions",
        json={"version": "1.0.0", "artifact_uri": "s3://models/compressor/1.0.0"},
    )
    v2 = client.post(
        f"/models/{model_id}/versions",
        json={"version": "1.1.0", "artifact_uri": "s3://models/compressor/1.1.0"},
    )
    assert v1.status_code == 201
    assert v2.status_code == 201

    versions = client.get(f"/models/{model_id}/versions").json()
    assert {v["version"] for v in versions} == {"1.0.0", "1.1.0"}
    assert all(v["stage"] == "DRAFT" and v["approved"] is False for v in versions)


def test_duplicate_model_name_conflicts(client, registered_model):
    response = client.post(
        "/models",
        json={
            "name": registered_model["name"],
            "owner": "Someone Else",
            "framework": "xgboost",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_duplicate_version_conflicts(client, registered_model):
    model_id = registered_model["id"]
    payload = {"version": "1.0.0", "artifact_uri": "s3://models/x/1.0.0"}
    first = client.post(f"/models/{model_id}/versions", json=payload)
    second = client.post(f"/models/{model_id}/versions", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


def test_get_missing_model_returns_404(client):
    response = client.get("/models/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"


def test_invalid_model_payload_returns_422(client):
    response = client.post("/models", json={"owner": "Someone"})
    assert response.status_code == 422


def test_approve_version(client, registered_model):
    """Acceptance scenario 2: Approve one version."""
    model_id = registered_model["id"]
    version = client.post(
        f"/models/{model_id}/versions",
        json={"version": "1.0.0", "artifact_uri": "s3://models/x/1.0.0"},
    ).json()

    approved = client.post(f"/models/{model_id}/versions/{version['id']}/approve")
    assert approved.status_code == 200
    body = approved.json()
    assert body["approved"] is True
    assert body["stage"] == "APPROVED"


def test_search_filters_model_list(client):
    client.post("/models", json={"name": "vibration-sensor-model", "owner": "A", "framework": "sklearn"})
    client.post("/models", json={"name": "temperature-forecaster", "owner": "B", "framework": "pytorch"})

    results = client.get("/models", params={"search": "vibration"}).json()
    assert len(results) == 1
    assert results[0]["name"] == "vibration-sensor-model"
