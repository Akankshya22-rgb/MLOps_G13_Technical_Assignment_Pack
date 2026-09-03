# ADR-0003: `create_all` schema setup instead of Alembic migrations

## Status
Accepted

## Context
The G13 expectations ask for "database migrations **or** documented schema setup" — an explicit
either/or. The schema here is five small tables with no data yet in production to migrate.

## Decision
Create tables via `SQLAlchemy.Base.metadata.create_all()` on application startup
(`app/database.py::init_db`), and document the schema through the ORM models themselves
(`app/models/`) plus this ADR, rather than introducing Alembic.

## Alternatives Considered
- **Alembic migrations**: the more production-realistic choice, and the natural next step once this
  schema needs to evolve under real data (see Follow-up). Introducing it now would add a
  `migrations/` directory and a versioning workflow for a schema that has had exactly one shape.

## Consequences
### Positive
- One less moving part for a reviewer to set up — `docker compose up --build` and the tables exist.
- `create_all` is idempotent, so it's safe to run on every startup.

### Negative
- No migration history, no safe path to alter an existing populated table without manual SQL or a
  volume reset. This is the direct trade-off the ADR is naming.

## Follow-up Actions
Introduce Alembic (`alembic init`, autogenerate a baseline revision matching the current models)
before the first schema change that must preserve existing data — i.e. before this goes anywhere
near a real deployment with real rows in it.
