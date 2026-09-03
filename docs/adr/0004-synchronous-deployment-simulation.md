# ADR-0004: Deployment pipeline runs synchronously in-request

## Status
Accepted

## Context
The brief asks for deployment status tracking, failure simulation, retry and rollback — behavior
that in a real system would be driven by an async worker calling out to a model-serving platform,
polling status over time. This assignment doesn't stand up a queue/broker, and the acceptance
scenarios need to be exercised deterministically in tests.

## Decision
`deployment_service._run_pipeline` transitions a deployment through
`REQUESTED → VALIDATING → DEPLOYING → SUCCEEDED|FAILED` synchronously, inside the same request and
DB transaction as the `POST /deployments` (or `/retry`) call, committing the final status and its
event log together. Failure is controlled explicitly via a `simulate_failure` flag on the request
body rather than randomized, so retry-after-failure is a deterministic, testable path rather than a
flaky one.

## Alternatives Considered
- **Randomized failure** (e.g. 20% chance): more "realistic" on the surface, but makes tests flaky
  or forces seeding a fake RNG — worse for the "deterministic fixtures and tests" expectation the
  G13 rubric explicitly calls out.
- **A real async worker (Celery/RQ) with a fake in-process broker**: closer to production shape, but
  a meaningfully larger amount of infrastructure (broker, worker process, result backend) for a
  simulation that still wouldn't call a real model-serving platform. Documented as the intended next
  step instead (see [architecture.md](../architecture.md#scaling)).

## Consequences
### Positive
- Every deployment/retry/rollback acceptance scenario is a single, fast, deterministic HTTP call —
  no polling, no sleep-based tests, no test flakiness from timing.
- The event timeline (`DeploymentEvent` rows) still models the real state machine a worker-based
  implementation would produce, so swapping in a real worker later doesn't change the API contract.

### Negative
- A slow "deploy" step would block the request thread in this implementation; not acceptable as-is
  for a real model-serving call that can take seconds to minutes.
- `attempt_count` and status are updated in one transaction rather than reflecting genuinely
  concurrent/long-running work.

## Follow-up Actions
Replace `_run_pipeline`'s inline execution with a task enqueued to a real worker, with
`POST /deployments` returning `202 Accepted` and the deployment starting in `REQUESTED`; the
Angular UI already polls-by-reload pattern (`Resource.reload()`) so it would only need a
"still in progress" state added to work against an async backend.
