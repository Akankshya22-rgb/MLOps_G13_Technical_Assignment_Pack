def _create_unapproved_version(client, model_id, version="1.0.0"):
    resp = client.post(
        f"/models/{model_id}/versions",
        json={"version": version, "artifact_uri": f"s3://models/x/{version}"},
    )
    assert resp.status_code == 201
    return resp.json()


def test_unapproved_version_cannot_deploy_to_production(client, registered_model):
    """Acceptance scenario 3: Prevent an unapproved version from Production deployment."""
    model_id = registered_model["id"]
    version = _create_unapproved_version(client, model_id)

    response = client.post(
        "/deployments",
        json={"model_id": model_id, "version_id": version["id"], "environment": "production"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "LIFECYCLE_ERROR"


def test_deploy_approved_version(client, registered_model, approved_version):
    """Acceptance scenario 4: Deploy an approved version."""
    model_id = registered_model["id"]
    response = client.post(
        "/deployments",
        json={"model_id": model_id, "version_id": approved_version["id"], "environment": "production"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "SUCCEEDED"

    version_after = client.get(f"/models/{model_id}/versions/{approved_version['id']}").json()
    assert version_after["stage"] == "PRODUCTION"


def test_retry_failed_deployment(client, registered_model, approved_version):
    """Acceptance scenario 6: Retry a failed deployment."""
    model_id = registered_model["id"]
    failed = client.post(
        "/deployments",
        json={
            "model_id": model_id,
            "version_id": approved_version["id"],
            "environment": "production",
            "simulate_failure": True,
        },
    ).json()
    assert failed["status"] == "FAILED"

    retried = client.post(f"/deployments/{failed['id']}/retry", json={"simulate_failure": False})
    assert retried.status_code == 200
    body = retried.json()
    assert body["status"] == "SUCCEEDED"
    assert body["attempt_count"] == 2


def test_cannot_retry_a_succeeded_deployment(client, registered_model, approved_version):
    model_id = registered_model["id"]
    deployment = client.post(
        "/deployments",
        json={"model_id": model_id, "version_id": approved_version["id"], "environment": "production"},
    ).json()

    response = client.post(f"/deployments/{deployment['id']}/retry")
    assert response.status_code == 422


def test_rollback_production_deployment(client, registered_model, approved_version):
    """Acceptance scenario 7: Roll back a Production deployment."""
    model_id = registered_model["id"]

    first_deployment = client.post(
        "/deployments",
        json={"model_id": model_id, "version_id": approved_version["id"], "environment": "production"},
    ).json()
    assert first_deployment["status"] == "SUCCEEDED"

    v2 = client.post(
        f"/models/{model_id}/versions",
        json={"version": "2.0.0", "artifact_uri": "s3://models/x/2.0.0"},
    ).json()
    client.post(f"/models/{model_id}/versions/{v2['id']}/approve")

    second_deployment = client.post(
        "/deployments",
        json={"model_id": model_id, "version_id": v2["id"], "environment": "production"},
    ).json()
    assert second_deployment["status"] == "SUCCEEDED"

    rollback = client.post(f"/deployments/{second_deployment['id']}/rollback")
    assert rollback.status_code == 200
    assert rollback.json()["status"] == "ROLLED_BACK"

    v2_after = client.get(f"/models/{model_id}/versions/{v2['id']}").json()
    v1_after = client.get(f"/models/{model_id}/versions/{approved_version['id']}").json()
    assert v2_after["stage"] == "STAGING"
    assert v1_after["stage"] == "PRODUCTION"


def test_rollback_without_prior_success_is_rejected(client, registered_model, approved_version):
    model_id = registered_model["id"]
    deployment = client.post(
        "/deployments",
        json={"model_id": model_id, "version_id": approved_version["id"], "environment": "production"},
    ).json()

    response = client.post(f"/deployments/{deployment['id']}/rollback")
    assert response.status_code == 422


def test_duplicate_deployment_requests_are_handled_safely(client, registered_model, approved_version):
    """Acceptance scenario 8: Handle duplicate deployment requests safely."""
    model_id = registered_model["id"]

    payload = {
        "model_id": model_id,
        "version_id": approved_version["id"],
        "environment": "production",
        "idempotency_key": "deploy-once-key",
    }
    first = client.post("/deployments", json=payload)
    second = client.post("/deployments", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


def test_missing_deployment_returns_clear_404(client):
    """Acceptance scenario 9: Surface API failures clearly."""
    response = client.get("/deployments/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert "does-not-exist" in body["error"]["message"]


def test_invalid_environment_returns_400(client, registered_model, approved_version):
    response = client.post(
        "/deployments",
        json={"model_id": registered_model["id"], "version_id": approved_version["id"], "environment": "canary"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_deployment_events_are_recorded(client, registered_model, approved_version):
    model_id = registered_model["id"]
    deployment = client.post(
        "/deployments",
        json={"model_id": model_id, "version_id": approved_version["id"], "environment": "staging"},
    ).json()

    detail = client.get(f"/deployments/{deployment['id']}").json()
    event_types = [e["event_type"] for e in detail["events"]]
    assert "deployment_requested" in event_types
    assert "deployment_completed" in event_types
