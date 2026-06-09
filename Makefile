.PHONY: help dev build stop logs shell-backend shell-db migrate seed test lint format

help:
	@echo ""
	@echo "  dev           Start all services in dev mode"
	@echo "  build         Build all Docker images"
	@echo "  stop          Stop all services"
	@echo "  logs          Tail logs"
	@echo "  shell-backend Open a shell inside the backend container"
	@echo "  shell-db      Open psql inside the db container"
	@echo "  migrate       Run Alembic migrations"
	@echo "  seed          Run seed scripts"
	@echo "  test          Run all tests"
	@echo "  lint          Run linters"
	@echo "  format        Auto-format code"
	@echo ""

dev:
	docker compose -f docker-compose.dev.yml up

build:
	docker compose -f docker-compose.dev.yml build

stop:
	docker compose -f docker-compose.dev.yml down

logs:
	docker compose -f docker-compose.dev.yml logs -f

shell-backend:
	docker compose -f docker-compose.dev.yml exec backend bash

shell-db:
	docker compose -f docker-compose.dev.yml exec db psql -U postgres -d github_analytics

migrate:
	docker compose -f docker-compose.dev.yml exec backend alembic upgrade head

seed:
	docker compose -f docker-compose.dev.yml exec backend python scripts/seed.py

test:
	docker compose -f docker-compose.dev.yml exec backend pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	docker compose -f docker-compose.dev.yml exec backend ruff check app/
	docker compose -f docker-compose.dev.yml exec backend mypy app/

format:
	docker compose -f docker-compose.dev.yml exec backend ruff format app/