.PHONY: init install-api install-web run dev lint test clean help ai-starter

# Ensure bash is used for commands that rely on 'source'
SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

# Environment setup
ENV_FILE := .env
ENV_EXAMPLE := .env.example

# Default target
help:
	@echo "Hobby Showcase - Available targets:"
	@echo "  init          - Initialize the project (install deps, setup DB, seed data)"
	@echo "  install-api   - Install Python backend dependencies"
	@echo "  install-web   - Install Node.js frontend dependencies"
	@echo "  run           - Run both API and web servers"
	@echo "  dev           - Run development servers with hot reload"
	@echo "  lint          - Run linters for all code"
	@echo "  test          - Run all tests"
	@echo "  clean         - Clean build artifacts and caches"
	@echo ""
	@echo "Database commands:"
	@echo "  db-init       - Initialize database with migrations"
	@echo "  db-seed       - Seed database with default data"
	@echo "  db-reset      - Reset database (WARNING: destructive)"
	@echo ""
	@echo "Docker commands:"
	@echo "  docker-up     - Start with Docker Compose"
	@echo "  docker-down   - Stop Docker Compose"
		@echo "  docker-build  - Build Docker images"
		@echo "  ai-starter    - Generate demo entries (starter seed)"

# Environment setup
$(ENV_FILE):
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Creating .env file from template..."; \
		cp $(ENV_EXAMPLE) $(ENV_FILE); \
		echo "Please edit .env file with your settings"; \
	fi

# Installation targets
install-api:
	@echo "Installing Python API dependencies..."
	python3 -m venv .venv
	. .venv/bin/activate; python -m pip install --upgrade pip setuptools wheel
	. .venv/bin/activate; pip install --prefer-binary --no-cache-dir -r apps/api/requirements.txt

install-web:
	@echo "Installing Node.js web dependencies..."
	cd apps/web && npm install

# Database targets
db-init: $(ENV_FILE)
	@echo "Initializing database..."
	source .venv/bin/activate && cd apps/api && alembic upgrade head && python3 -m app.cli init

db-seed: $(ENV_FILE)
	@echo "Seeding database..."
	source .venv/bin/activate && cd apps/api && python3 -m app.cli init

db-reset: $(ENV_FILE)
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f data/app.db; \
		echo "\nDatabase deleted. Run 'make db-init' to recreate."; \
	else \
		echo "\nAborted."; \
	fi

# Main initialization
init: $(ENV_FILE) install-api install-web db-init
	@echo "Project initialized successfully!"
	@echo "Run 'make run' to start the application"

# Development servers
run: $(ENV_FILE)
	@echo "Starting production servers..."
	@trap 'kill 0' INT; \
	(source .venv/bin/activate && cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port 8000) & \
	(cd apps/web && npm run build && PORT=3000 npm start) & \
	wait

dev: $(ENV_FILE)
	@echo "Starting development servers..."
	@trap 'kill 0' INT; \
	(source .venv/bin/activate && cd apps/api && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) & \
	(cd apps/web && PORT=3000 npm run dev) & \
	wait

# Linting
lint:
	@echo "Running linters..."
	source .venv/bin/activate && cd apps/api && ruff check . && black --check .
	cd apps/web && npm run lint

lint-fix:
	@echo "Fixing linting issues..."
	source .venv/bin/activate && cd apps/api && ruff check --fix . && black .
	cd apps/web && npm run lint --fix

# Testing
test:
	@echo "Running tests..."
	source .venv/bin/activate && cd apps/api && python -m pytest
	cd apps/web && npx playwright test

test-api:
	@echo "Running API tests..."
	source .venv/bin/activate && cd apps/api && python -m pytest

test-web:
	@echo "Running web tests..."
	cd apps/web && npx playwright test

# Docker
docker-build:
	docker compose build

docker-up: $(ENV_FILE)
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
		docker compose logs -f

# AI-like starter seed
ai-starter: $(ENV_FILE)
		@echo "Generating demo entries..."
		source .venv/bin/activate && cd apps/api && python3 -m app.cli starter --count 10

# Export/Import
export-data:
	@echo "Exporting data..."
	@mkdir -p exports
	@echo "Creating backup archive..."
	@cd exports && zip -r hobby-showcase-backup.zip ../data ../uploads 2>/dev/null || true
	@echo "Data exported to exports/hobby-showcase-backup.zip"

# Cleanup
clean:
	@echo "Cleaning up..."
	rm -rf apps/api/__pycache__
	rm -rf apps/api/.pytest_cache
	rm -rf apps/api/build
	rm -rf apps/api/dist
	rm -rf apps/api/*.egg-info
	rm -rf apps/web/.next
	rm -rf apps/web/node_modules/.cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "Cleanup complete!"

# Quick development setup for new contributors
quickstart: init
	@echo ""
	@echo "🎉 Hobby Showcase is ready!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your settings"
	@echo "2. Run 'make dev' to start development servers"
	@echo "3. Open http://localhost:3000 in your browser"
	@echo "4. Login with the password from your .env file"
	@echo ""
