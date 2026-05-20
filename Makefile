.PHONY: up down build seed migrate logs backend frontend

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

# Run Alembic migration (inside backend container)
migrate:
	docker compose exec backend alembic upgrade head

# Seed initial data (admin user, methods, quality grades)
seed:
	docker compose exec backend python -m app.utils.seed

# Backend-only dev (without Docker)
backend-dev:
	cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload --port 8000

# Frontend-only dev (without Docker)
frontend-dev:
	cd frontend && npm install && npm run dev

# Run tests
test:
	docker compose exec backend pytest -v

# Generate new Alembic migration
migration-new:
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"
