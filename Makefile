# ====== DEVELOPMENT ======
.PHONY: dev dev-docker docker-build base-dev
dev:
	uv run src/main.py
dev-docker:
	docker compose up
docker-build:
	docker compose build
base-dev:
	docker compose up postgres redis dozzle adminer -d

stop-base-dev:
	docker compose stop postgres redis dozzle adminer

full-dev: base-dev dev

# ====== CODE QUALITY ======
.PHONY: check lint-format type-check
lint-format:
	uv run ruff format .
	uv run ruff check . --fix
type-check:
	uv run mypy src
check: lint-format type-check

# ====== TESTING ======
.PHONY: test test-verbose test-coverage test-watch test-specific
test:
	ENVIRONMENT=testing uv run pytest

test-verbose:
	ENVIRONMENT=testing uv run pytest -v

test-coverage:
	ENVIRONMENT=testing uv run pytest --cov=src --cov-report=html --cov-report=term-missing

test-specific:
	@if [ -z "$(path)" ]; then \
		echo "Usage: make test-specific path='path/to/test'"; \
		exit 1; \
	fi
	ENVIRONMENT=testing uv run pytest "$(path)" -v

# ====== DATABASE ======
.PHONY: db-generate db-upgrade db-downgrade db-current db-history db-reset
db-generate:
	@if [ -z "$(message)" ]; then \
		echo "Usage: make db-generate message='Your migration message'"; \
		exit 1; \
	fi
	PYTHONPATH=src/ uv run alembic revision --autogenerate -m "$(message)"

db-upgrade:
	PYTHONPATH=src/ uv run alembic upgrade head

db-downgrade:
	@if [ -z "$(revision)" ]; then \
		echo "Usage: make db-downgrade revision='target_revision'"; \
		exit 1; \
	fi
	PYTHONPATH=src/ uv run alembic downgrade "$(revision)"

db-current:
	PYTHONPATH=src/ uv run alembic current

db-history:
	PYTHONPATH=src/ uv run alembic history --verbose

db-reset:
	@echo "WARNING: This will delete all data and reset the database!"
	@read -p "Are you sure? (y/N): " confirm && [ "$confirm" = "y" ]
	PYTHONPATH=src/ uv run alembic downgrade base
	PYTHONPATH=src/ uv run alembic upgrade head

db-shell:
	docker compose exec postgres psql -U satsbell -d satsbell

# ====== UTILITIES ======
.PHONY: install clean logs help
install:
	uv sync

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

help:
	@echo "Available commands:"
	@echo "  Development:"
	@echo "    dev          - Run API locally"
	@echo "    dev-docker   - Run full stack with Docker"
	@echo "    docker-build - Build containers"
	@echo "    base-dev     - Run only supporting services (DB, Redis, etc.)"
	@echo "    stop-base-dev - Stop supporting services"
	@echo "    full-dev     - Run supporting services and API locally"
	@echo ""
	@echo "  Code Quality:"
	@echo "    check        - Run all code quality checks"
	@echo "    lint-format  - Format and fix code"
	@echo "    type-check   - Run type checking"
	@echo ""
	@echo "  Database:"
	@echo "    db-generate message='msg'  - Generate new migration"
	@echo "    db-upgrade               - Apply migrations"
	@echo "    db-current               - Show current migration"
	@echo "    db-history               - Show migration history"
	@echo "    db-downgrade revision=X  - Rollback to revision"
	@echo "    db-reset                 - Reset database (DESTRUCTIVE)"
	@echo "    db-shell                 - Open PostgreSQL shell"
	@echo ""
	@echo "  Testing:"
	@echo "    test         - Run all tests"
	@echo "    test-verbose - Run all tests with verbose output"
	@echo "    test-coverage - Run tests with coverage report"
	@echo "    test-specific path='path/to/test' - Run specific test"
	@echo ""
	@echo "  Utilities:"
	@echo "    install - Install dependencies"
	@echo "    clean   - Clean Python cache files"
	@echo "    help    - Show this help"
