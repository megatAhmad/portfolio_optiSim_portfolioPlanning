# Portfolio OptiSim - Development Makefile
# Usage: make <target>
#
# All backend commands run from the backend/ directory.
# Ensure you have activated your virtual environment before running.

.PHONY: help dev test lint format typecheck migrate ci docker-up docker-down \
        install clean worker db-reset coverage

SHELL := /bin/bash
BACKEND_DIR := backend
FRONTEND_DIR := frontend

# Default target
help: ## Show this help message
	@echo "Portfolio OptiSim - Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

install: ## Install all dependencies (backend dev + frontend)
	cd $(BACKEND_DIR) && pip install -e ".[dev]"
	cd $(FRONTEND_DIR) && npm install

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dev: ## Start FastAPI development server with hot reload
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker: ## Start Celery worker for async tasks
	cd $(BACKEND_DIR) && celery -A app.tasks worker --loglevel=info --concurrency=4

dev-frontend: ## Start Next.js development server
	cd $(FRONTEND_DIR) && npm run dev

# ---------------------------------------------------------------------------
# Code Quality
# ---------------------------------------------------------------------------

lint: ## Run ruff linter on backend code
	cd $(BACKEND_DIR) && ruff check .

lint-fix: ## Run ruff linter with auto-fix
	cd $(BACKEND_DIR) && ruff check . --fix

format: ## Format backend code with ruff
	cd $(BACKEND_DIR) && ruff format .

format-check: ## Check formatting without making changes
	cd $(BACKEND_DIR) && ruff format --check .

typecheck: ## Run mypy strict type checking on backend
	cd $(BACKEND_DIR) && mypy app/

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: ## Run all backend tests
	cd $(BACKEND_DIR) && pytest

test-unit: ## Run unit tests only
	cd $(BACKEND_DIR) && pytest tests/unit/ -v

test-integration: ## Run integration tests only
	cd $(BACKEND_DIR) && pytest tests/integration/ -v

test-fast: ## Run tests, stop on first failure
	cd $(BACKEND_DIR) && pytest -x -v

coverage: ## Run tests with coverage report
	cd $(BACKEND_DIR) && pytest --cov=app --cov-report=term-missing --cov-report=html

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate: ## Apply all pending database migrations
	cd $(BACKEND_DIR) && alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(MSG)"

migrate-downgrade: ## Downgrade one migration step
	cd $(BACKEND_DIR) && alembic downgrade -1

migrate-history: ## Show migration history
	cd $(BACKEND_DIR) && alembic history --verbose

db-reset: ## Drop and recreate the database (DESTRUCTIVE - development only)
	cd $(BACKEND_DIR) && alembic downgrade base && alembic upgrade head

# ---------------------------------------------------------------------------
# CI Pipeline (run before committing)
# ---------------------------------------------------------------------------

ci: ## Run full CI pipeline: lint, format check, typecheck, tests with coverage
	@echo "=========================================="
	@echo "  Running CI pipeline"
	@echo "=========================================="
	cd $(BACKEND_DIR) && ruff check .
	@echo "--- Lint passed ---"
	cd $(BACKEND_DIR) && ruff format --check .
	@echo "--- Format check passed ---"
	cd $(BACKEND_DIR) && mypy app/
	@echo "--- Type check passed ---"
	cd $(BACKEND_DIR) && pytest --cov=app --cov-report=term-missing
	@echo "=========================================="
	@echo "  CI pipeline completed successfully"
	@echo "=========================================="

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-up: ## Start all services via Docker Compose
	docker-compose up -d

docker-down: ## Stop all Docker Compose services
	docker-compose down

docker-build: ## Build all Docker images
	docker-compose build

docker-logs: ## Follow Docker Compose logs
	docker-compose logs -f

docker-restart: ## Restart all Docker services
	docker-compose down && docker-compose up -d

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: ## Remove build artifacts, caches, and temporary files
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND_DIR) -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND_DIR) -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND_DIR) -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	find $(BACKEND_DIR) -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Cleaned build artifacts."
