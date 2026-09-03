# Test Strategy

## Unit Tests (`backend/tests/unit/`)

Pure-Python tests against the domain layer, no DB or HTTP:

- `test_lifecycle.py` — every allowed/disallowed `LifecycleStage` transition, including that a
  same-stage "transition" is a no-op.
- `test_deployment_rules.py` — deployment eligibility (unapproved version blocked, `DRAFT` blocked
  even if `approved=True`, approved version deployable to both environments), retry only from
  `FAILED`, rollback only from `SUCCEEDED`. Uses a `FakeVersion` stand-in rather than the ORM class,
  so these run with zero DB setup.
- `test_metric_service.py` — the `HEALTHY`/`DEGRADED`/`UNHEALTHY` classification thresholds, via a
  `FakeMetric` stand-in.

## API / Integration Tests (`backend/tests/integration/`)

Run against a real (in-memory SQLite) database through FastAPI's `TestClient`, exercising the
actual HTTP layer, error mapping, and persistence together:

- `test_models_api.py` — registration, duplicate name/version conflicts (`409`), missing-model
  `404`, malformed payload `422`, approval, search filtering.
- `test_deployments_api.py` — the full deploy/retry/rollback lifecycle, unapproved-version block,
  idempotency-key dedup, in-flight duplicate `409`, event-timeline recording, clear 404 messages.
- `test_metrics_api.py` — summary + history shape, per-version/environment filtering, 404 for an
  unknown model.
- `test_health.py` — `/health` reports DB connectivity.

Fixtures (`conftest.py`) give each test a fresh in-memory SQLite database via a
`get_db` dependency override, so tests never touch a real file or share state — this is what makes
them deterministic and safe to run in parallel or in CI without a Postgres instance.

**Coverage**: 97% line coverage across `app/` as of this submission (`pytest --cov=app`); CI enforces
a `--cov-fail-under=85` floor so it can't silently regress.

## Angular Tests (`frontend/src/**/*.spec.ts`)

- **Services** (`model.service.spec.ts`, `deployment.service.spec.ts`): `HttpClientTestingModule` +
  `HttpTestingController` verify the exact request made (method, URL, params, body) without a real
  backend.
- **Components**:
  - `status-chip.component.spec.ts` — tone mapping for known and unknown statuses.
  - `model-list.component.spec.ts` — loading state, populated render, empty state, error state (via
    a flushed `500` with the platform's error envelope), and the create-form toggle. This is the one
    component test suite that walks all four UI states (loading/empty/success/error) called for in
    the brief; the same `Resource<T>` pattern backs every other page.
  - `app.component.spec.ts` — shell renders and navigation links are present.

Run with `npx ng test --watch=false --browsers=ChromeHeadless` (see `Makefile`'s `frontend-test`).

## End-to-End Scenario

Covered as a single integration test path across `test_models_api.py` + `test_deployments_api.py`:
register model → register two versions → approve one → block the other from production → deploy the
approved one → view its metrics → retry a simulated failure → roll back a production deployment.
Manually verified the same path through the Angular UI end-to-end (register → approve → deploy →
monitor → rollback) against a running backend.

## CI

`.github/workflows/ci.yml` runs three jobs on every push/PR: backend (ruff lint + pytest with the
coverage floor), frontend (Karma unit tests headless + a production build), and a docker-build
validation job that builds both images from the Dockerfiles used by `docker-compose.yml`.

## Known Gaps

- No Cypress/Playwright browser E2E suite — the "register → deploy → monitor → rollback" path is
  covered at the API level and was verified manually in the browser, but isn't automated end-to-end
  through the rendered UI.
- No load/performance testing.
- No mutation testing or property-based testing (e.g. Hypothesis) on the lifecycle state machine,
  though its small transition table is fully enumerated by `test_lifecycle.py`.
