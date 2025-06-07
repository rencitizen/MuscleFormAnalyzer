# Makefile for BodyScale Pose Analyzer

.PHONY: help install dev build clean test docker-up docker-down setup

# Default target
help:
	@echo "BodyScale Pose Analyzer - Development Commands"
	@echo "============================================="
	@echo "make install      - Install all dependencies"
	@echo "make dev          - Start development servers"
	@echo "make build        - Build for production"
	@echo "make clean        - Clean build artifacts"
	@echo "make test         - Run all tests"
	@echo "make docker-up    - Start Docker containers"
	@echo "make docker-down  - Stop Docker containers"
	@echo "make setup        - Initial project setup"
	@echo ""

# Setup Python virtual environment
venv:
	python3 -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

# Install all dependencies
install: venv
	. venv/bin/activate && pip install -r requirements.txt
	npm install
	cd frontend && npm install

# Setup local environment
setup:
	cp .env.example .env.local
	make install
	@echo "Setup complete! Edit .env.local with your settings"

# Start development servers
dev:
	npm run dev

# Start individual servers
dev-backend:
	. venv/bin/activate && python app.py

dev-frontend:
	cd frontend && npm run dev

# Build for production
build:
	cd frontend && npm run build

# Clean build artifacts
clean:
	rm -rf frontend/node_modules frontend/.next
	rm -rf node_modules
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf venv
	rm -f *.pyc */*.pyc */*/*.pyc
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete

# Run tests
test:
	. venv/bin/activate && python -m pytest
	cd frontend && npm test

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

# Database commands
db-init:
	. venv/bin/activate && python init_database.py

db-migrate:
	@echo "Database migration not implemented yet"

# ML commands
ml-train:
	. venv/bin/activate && python ml/scripts/train_model.py --days 30

ml-synthetic:
	. venv/bin/activate && python ml/data_collection/synthetic_data_generator.py

# Utility commands
format:
	. venv/bin/activate && black .
	cd frontend && npm run format

lint:
	. venv/bin/activate && flake8 .
	cd frontend && npm run lint

# Production deployment
deploy:
	@echo "Deployment script not implemented yet"

# Check environment
check:
	@echo "Checking environment..."
	@python3 --version
	@node --version
	@npm --version
	@echo "Environment check complete"