.PHONY: up down backend-install backend-test backend-run frontend-install frontend-test frontend-run seed

up:
	docker compose up --build

down:
	docker compose down -v

backend-install:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

backend-test:
	cd backend && . .venv/bin/activate && python -m pytest

backend-run:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend-install:
	cd frontend && npm ci

frontend-test:
	cd frontend && npx ng test --watch=false --browsers=ChromeHeadless

frontend-run:
	cd frontend && npx ng serve

seed:
	cd backend && . .venv/bin/activate && python ../scripts/seed_data.py
