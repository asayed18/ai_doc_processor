# AI Document Processor Makefile
# Provides commands to run frontend, backend, and both services

.PHONY: help install install-backend install-frontend backend frontend dev start stop clean test build format format-check lint quality

# Default target
help:
	@echo "🚀 AI Document Processor - Available Commands:"
	@echo ""
	@echo "  make install       - Install all dependencies (backend + frontend)"
	@echo "  make install-backend - Install backend dependencies with pipenv"
	@echo "  make install-frontend - Install frontend dependencies only"
	@echo "  make install-dev   - Install backend dev dependencies with pipenv"
	@echo "  make setup         - Full project setup (install + migrate)"
	@echo ""
	@echo "  make backend       - Start backend server (FastAPI)"
	@echo "  make frontend      - Start frontend server (Next.js)"
	@echo "  make dev           - Start both backend and frontend concurrently"
	@echo "  make start         - Alias for 'make dev'"
	@echo ""
	@echo "  make build         - Build frontend for production"
	@echo "  make prod-backend  - Start backend with gunicorn"
	@echo "  make prod-frontend - Start frontend in production mode"
	@echo ""
	@echo "  make stop          - Stop all running services"
	@echo "  make clean         - Clean node_modules and Python cache"
	@echo "  make test          - Run tests (when available)"
	@echo "  make shell         - Enter pipenv shell for backend development"
	@echo ""
	@echo "🔧 Process Management:"
	@echo "  make status        - Check backend and frontend status"
	@echo "  make check-ports   - Show what's running on ports 8000/3000"
	@echo "  make kill-ports    - Kill processes on ports 8000/3000"
	@echo "  make restart       - Stop and restart all services"
	@echo ""
	@echo "🎨 Code Quality:"
	@echo "  make format        - Format code with Black and isort"
	@echo "  make lint          - Run linting with flake8 and mypy"
	@echo "  make format-check  - Check if code is properly formatted"
	@echo "  make quality       - Run all code quality checks"
	@echo ""
	@echo "🗄️  Database & Migrations:"
	@echo "  make migrate       - Run pending database migrations"
	@echo "  make migration     - Create a new migration (requires MESSAGE)"
	@echo "  make migration-auto - Auto-generate migration from model changes"
	@echo "  make db-upgrade    - Alias for migrate"
	@echo "  make db-downgrade  - Downgrade database by one revision"
	@echo "  make db-current    - Show current migration revision"
	@echo "  make db-history    - Show migration history"
	@echo ""
	@echo "🔗 URLs:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

# Install all dependencies
install: install-backend install-frontend migrate
	@echo "✅ All dependencies installed and database migrated successfully!"

# Full project setup
setup: install
	@echo "🚀 Project setup complete! Ready to start development."

# Install backend dependencies
install-backend:
	@echo "📡 Installing backend dependencies with pipenv..."
	@cd backend && pipenv install

# Install backend development dependencies
install-dev:
	@echo "📡 Installing backend dev dependencies with pipenv..."
	@cd backend && pipenv install --dev

# Install frontend dependencies  
install-frontend:
	@echo "🌐 Installing frontend dependencies..."
	@cd frontend && npm install

# Start backend server
backend:
	@echo "📡 Starting AI Document Processor Backend..."
	@echo "🔗 Backend will be available at: http://localhost:8000"
	@echo "🔗 API Documentation at: http://localhost:8000/docs"
	@echo "Checking for existing processes on port 8000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@cd backend && pipenv run python main.py

# Start frontend server
frontend:
	@echo "🌐 Starting AI Document Processor Frontend..."
	@echo "🔗 Frontend will be available at: http://localhost:3000"
	@echo "Checking for existing processes on port 3000..."
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@cd frontend && npm run dev

# Start both services concurrently (requires 'concurrently' or manual process management)
dev: install stop
	@echo "🚀 Starting AI Document Processor Application..."
	@echo "This will start both backend and frontend services."
	@echo ""
	@echo "🔗 Frontend: http://localhost:3000"
	@echo "🔗 Backend:  http://localhost:8000"
	@echo "🔗 API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "📁 Test documents are in: ./data/"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@echo ""
	@echo "Starting backend in background..."
	@cd backend && pipenv run python main.py & echo $$! > ../.backend.pid
	@sleep 3
	@echo "Starting frontend..."
	@cd frontend && npm run dev & echo $$! > ../.frontend.pid
	@echo ""
	@echo "✅ Both services started! Use 'make stop' to stop them."
	@wait

# Alias for dev
start: dev

# Stop all services
stop:
	@echo "🛑 Stopping all services..."
	@if [ -f .backend.pid ]; then \
		kill `cat .backend.pid` 2>/dev/null || true; \
		rm -f .backend.pid; \
		echo "📡 Backend stopped"; \
	fi
	@if [ -f .frontend.pid ]; then \
		kill `cat .frontend.pid` 2>/dev/null || true; \
		rm -f .frontend.pid; \
		echo "🌐 Frontend stopped"; \
	fi
	@pkill -f "python.*main.py" 2>/dev/null || true
	@pkill -f "next-server" 2>/dev/null || true
	@pkill -f "uvicorn" 2>/dev/null || true
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@echo "✅ All services stopped"

# Build frontend for production
build:
	@echo "🏗️  Building frontend for production..."
	@cd frontend && npm run build

# Start backend with gunicorn for production
prod-backend:
	@echo "📡 Starting backend with gunicorn..."
	@cd backend && pipenv run gunicorn main:app --host 0.0.0.0 --port 8000

# Start frontend in production mode
prod-frontend: build
	@echo "🌐 Starting frontend in production mode..."
	@cd frontend && npm start

# Clean build artifacts and dependencies
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf frontend/node_modules
	@rm -rf frontend/.next
	@rm -f .backend.pid .frontend.pid
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned up successfully"

# Run tests (placeholder for future implementation)
test:
	@echo "🧪 Running tests..."
	@echo "Tests not yet implemented"

# Development helpers
check-backend:
	@echo "🔍 Checking backend status..."
	@curl -s http://localhost:8000/ || echo "❌ Backend not running"

check-frontend:
	@echo "🔍 Checking frontend status..."
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend running" || echo "❌ Frontend not running"

status: check-backend check-frontend

# Check what's running on ports
check-ports:
	@echo "🔍 Checking what's running on application ports..."
	@echo "Port 8000 (Backend):"
	@lsof -i :8000 || echo "   Nothing running on port 8000"
	@echo "Port 3000 (Frontend):"
	@lsof -i :3000 || echo "   Nothing running on port 3000"

# Kill processes on specific ports
kill-ports:
	@echo "🛑 Killing processes on ports 8000 and 3000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "   No processes on port 8000"
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "   No processes on port 3000"
	@echo "✅ Ports cleared"

# Quick restart
restart: stop start

# Enter pipenv shell for backend development
shell:
	@echo "🐍 Entering pipenv shell for backend development..."
	@cd backend && pipenv shell

# Database migration commands
migrate:
	@echo "🗄️  Running pending database migrations..."
	@cd backend && pipenv run alembic upgrade head

migration:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Please provide a migration message: make migration MESSAGE='your message'"; \
		exit 1; \
	fi
	@echo "🗄️  Creating new migration: $(MESSAGE)"
	@cd backend && pipenv run alembic revision -m "$(MESSAGE)"

migration-auto:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Please provide a migration message: make migration-auto MESSAGE='your message'"; \
		exit 1; \
	fi
	@echo "🗄️  Auto-generating migration: $(MESSAGE)"
	@cd backend && pipenv run alembic revision --autogenerate -m "$(MESSAGE)"

db-upgrade: migrate

db-downgrade:
	@echo "🗄️  Downgrading database by one revision..."
	@cd backend && pipenv run alembic downgrade -1

db-current:
	@echo "🗄️  Current database revision:"
	@cd backend && pipenv run alembic current

db-history:
	@echo "🗄️  Migration history:"
	@cd backend && pipenv run alembic history

# Code Quality Commands
format:
	@echo "🎨 Formatting code with Black and isort..."
	cd backend && pipenv run black .
	cd backend && pipenv run isort .

format-check:
	@echo "🔍 Checking code formatting..."
	cd backend && pipenv run black --check --diff .
	cd backend && pipenv run isort --check-only --diff .

lint:
	@echo "🔍 Running linting and type checking..."
	cd backend && pipenv run flake8 .
	cd backend && pipenv run mypy .

quality: format-check lint
	@echo "✅ All code quality checks completed"