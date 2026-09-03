# ADR-0001: Backend framework — FastAPI over Flask/Django

## Status
Accepted

## Context
The brief asks for a Python backend with typed requests/responses, validation, consistent errors,
and generated API documentation, alongside SQLAlchemy for persistence.

## Decision
Use **FastAPI** with **Pydantic v2** models for request/response schemas and **SQLAlchemy 2.0**
(typed `Mapped[...]` style) for the ORM.

## Alternatives Considered
- **Flask**: minimal and familiar, but request/response typing and OpenAPI generation would need
  extra libraries (Marshmallow/flask-smorest) bolted on to reach parity with what FastAPI gives out
  of the box.
- **Django + DRF**: batteries-included (admin, ORM, auth) but heavier than this scope needs, and its
  ORM would replace SQLAlchemy rather than pair with it as the brief's stack suggests.

## Consequences
### Positive
- Request/response validation, `422` error bodies, and interactive docs (`/docs`, `/redoc`,
  `/openapi.json`) come for free from Pydantic type annotations — no separate schema library.
- `TestClient` (Starlette) makes integration testing the real HTTP layer fast and dependency-light.
- Async-ready if a future change needs it (not currently used — routes are sync since SQLAlchemy is
  used in sync mode here).

### Negative
- Smaller ecosystem than Django for things this project doesn't need yet (admin UI, built-in auth) —
  acceptable since those aren't in scope.

## Follow-up Actions
None.
