# Known Limitations & Future Improvements

## Known Limitations

- **No authentication/authorization.** Anyone with network access can register models, approve
  versions, or deploy to production. There's no concept of a user, role, or audit-by-who.
- **No async worker/queue.** The deployment "pipeline" runs synchronously inside the HTTP request
  (see [ADR-0004](adr/0004-synchronous-deployment-simulation.md)). It's deliberately fast and
  deterministic for this assignment, but a real deploy step (calling a model-serving platform) can
  take seconds-to-minutes and should not block a request thread.
- **No real model-serving integration.** `artifact_uri` is stored but nothing actually loads or
  serves the artifact; deployment is a state-machine simulation, not a real rollout.
- **Schema managed by `create_all`, not migrations.** Table creation is idempotent
  (`Base.metadata.create_all`) but there's no migration history — adding a column to an existing
  Postgres volume requires a manual `ALTER TABLE` or a wipe. See
  [ADR-0003](adr/0003-schema-management.md).
- **Metrics have no ingestion API.** They're loaded by `scripts/seed_data.py` directly into the
  database for demo purposes; there's no `POST` endpoint for a real monitoring pipeline to push
  samples yet.
- **No rate limiting or request throttling.**
- **No multi-tenancy.** All models/deployments live in one flat namespace; there's no "plant" or
  "org" boundary despite the brief's "many models across plants" framing.
- **No pagination.** `GET /models` and `GET /deployments` return full result sets; fine at demo
  scale, not at fleet scale.
- **Rollback is single-step.** It reverts to the immediately preceding successful deployment for
  that model+environment, not to an arbitrary point in history.
- **No browser E2E suite** (Cypress/Playwright) — see [test-strategy.md](test-strategy.md).

## Future Improvements

- Add OAuth2/OIDC in front of the API and environment-scoped roles (e.g. only a "release manager"
  role may deploy to `production`), enforced in `deployment_service`.
- Move the deploy pipeline to a real queue (Celery/RQ/cloud task queue) with a status-polling or
  websocket update instead of a synchronous response.
- Introduce Alembic migrations once the schema needs to evolve under real data.
- Add a metrics-ingestion endpoint and swap the CSV-seeded demo data for a real streaming source.
- Add `/v1` API versioning ahead of the first breaking change.
- Add an audit log distinct from `deployment_events` (who approved/deployed/rolled back, not just
  what happened).
- Browser-level E2E tests (Playwright) covering the full register → approve → deploy → rollback
  flow through the rendered Angular app, plus visual regression on the monitoring dashboard.
