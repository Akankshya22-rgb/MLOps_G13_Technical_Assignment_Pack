# API Design

Interactive docs are served by FastAPI at `/docs` (Swagger UI) and `/redoc` when the backend is
running, and the raw schema at `/openapi.json`.

## Conventions

- **Typed contracts**: every request/response body is a Pydantic model (`backend/app/schemas/`).
  FastAPI validates incoming bodies against these and returns `422` with field-level detail on
  failure.
- **Errors**: every handled error returns the same shape, regardless of endpoint:

  ```json
  { "error": { "code": "NOT_FOUND", "message": "Model 'x' was not found.", "details": { "model_id": "x" } } }
  ```

  | HTTP status | `code`             | Meaning |
  |---|---|---|
  | 400 | `VALIDATION_ERROR` | Well-formed request, invalid value (e.g. unsupported environment) |
  | 404 | `NOT_FOUND`        | Referenced model/version/deployment does not exist |
  | 409 | `CONFLICT`         | Duplicate name/version, or a deployment already in flight |
  | 422 | `LIFECYCLE_ERROR`  | Request is well-formed but violates a domain rule (e.g. deploying an unapproved version) |
  | 422 | (FastAPI default) | Pydantic body validation failure |

  This is implemented as one exception handler (`app/main.py`) over one exception hierarchy
  (`app/errors.py`), so new endpoints get consistent errors for free.
- **IDs**: all resource IDs are server-generated UUIDs (strings).
- **Timestamps**: UTC, ISO-8601.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness + DB connectivity check |
| POST | `/models` | Register a model (409 if name taken) |
| GET | `/models?search=` | List models, optional case-insensitive search across name/owner/framework/tags |
| GET | `/models/{model_id}` | Model detail, including its versions |
| POST | `/models/{model_id}/versions` | Register a version at stage `DRAFT` (409 if version exists) |
| GET | `/models/{model_id}/versions` | List a model's versions |
| GET | `/models/{model_id}/versions/{version_id}` | Version detail |
| POST | `/models/{model_id}/versions/{version_id}/approve` | Promote `DRAFT`/`VALIDATED` → `APPROVED` |
| GET | `/models/{model_id}/metrics?version=&environment=&limit=` | Monitoring summaries + history |
| POST | `/deployments` | Request a deployment (see below) |
| GET | `/deployments?model_id=&environment=&status=` | List/filter deployments |
| GET | `/deployments/{deployment_id}` | Deployment detail, including its event timeline |
| POST | `/deployments/{deployment_id}/retry` | Retry a `FAILED` deployment |
| POST | `/deployments/{deployment_id}/rollback` | Roll back a `SUCCEEDED` deployment |

This is a resource-oriented superset of the brief's minimum API list — `approve`, `versions/{id}`,
and `deployments/{id}/events`-via-detail were added because the acceptance scenarios ("approve a
version", "surface failures clearly") need them.

### `POST /deployments`

```json
{
  "model_id": "…",
  "version_id": "…",
  "environment": "staging | production",
  "idempotency_key": "optional-client-key",
  "simulate_failure": false
}
```

- `idempotency_key`: replaying the same key returns the original deployment (`201`, same body) —
  this is what protects against a double-click or a retried HTTP client.
- Independently, a second request for the same `(model_id, version_id, environment)` while one is
  still `REQUESTED`/`VALIDATING`/`DEPLOYING` is rejected with `409 CONFLICT`, even without an
  idempotency key.
- `simulate_failure`: a testing hook (also on `/retry`) so failure and retry can be exercised
  deterministically without a flaky random failure rate — see
  [ADR-0004](adr/0004-synchronous-deployment-simulation.md).
- Deployment to `production` requires `version.approved == true` **and** a stage of `APPROVED`,
  `STAGING` or `PRODUCTION`; violating this returns `422 LIFECYCLE_ERROR`, not `400`, because the
  request is valid input that conflicts with domain state.

## Versioning

Not yet versioned (no `/v1` prefix). For a real rollout, the recommendation is a URL path prefix
(`/v1/...`) introduced at the same time as the second breaking change, rather than upfront — see
[known-limitations.md](known-limitations.md).
