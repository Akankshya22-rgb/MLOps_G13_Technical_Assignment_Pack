# ADR-0002: PostgreSQL in Docker, SQLite for local dev and tests

## Status
Accepted

## Context
The brief lists "PostgreSQL/SQLite" as acceptable, and the seed `docker-compose.seed.yml` already
wires a Postgres service. Tests need to run fast, isolated, and without any external service.

## Decision
- **Docker Compose / "production-like" runs**: PostgreSQL 16, matching the seed artifact.
- **Local dev without Docker**: SQLite file, anchored to `backend/mlops.db` regardless of the
  process's working directory (see `app/config.py`), so `uvicorn` and `scripts/seed_data.py` always
  agree on which file they're using.
- **Tests**: SQLite **in-memory**, created fresh per test via a `get_db` dependency override
  (`tests/conftest.py`) — never the dev file, never Postgres.

SQLAlchemy is the abstraction that makes this free: the same models and queries run against both
engines with no code branching, only a `connect_args={"check_same_thread": False}` tweak for SQLite.

## Alternatives Considered
- **Postgres everywhere, including tests**: more production-realistic, but adds a service dependency
  to `pytest` and slows the suite; ruled out in favor of fast, hermetic tests. In CI, that trade-off
  costs nothing observable in this project's usage (Postgres and SQLite agree on everything the
  domain layer relies on: transactions, unique constraints, joins).
- **SQLite everywhere, including Docker Compose**: simplest possible setup, but drops the
  Postgres-specific behavior worth demonstrating for a submission targeting a "real" deployment.

## Consequences
### Positive
- Zero external dependencies to run `pytest`.
- One codebase, two backends, no ORM-specific branches.

### Negative
- A behavior difference that only manifests under Postgres (e.g. certain constraint semantics) would
  not be caught by the test suite. Not observed in this codebase's usage; worth keeping in mind if
  schema complexity grows.

## Follow-up Actions
If the schema grows enough that Postgres-specific behavior matters, add a docker-compose-backed test
job in CI that runs the integration suite against real Postgres as a second pass.
