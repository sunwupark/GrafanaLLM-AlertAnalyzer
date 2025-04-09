.PHONY: setup test lint format run docker-build docker-run clean all help

PYTHON = python
PIP = pip
PYTEST = pytest
FLAKE8 = flake8
BLACK = black
ISORT = isort
MYPY = mypy
DOCKER = docker

# Basic commands
help:
	@echo "Available commands:"
	@echo "  make setup      - Setup development environment and install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Check code with linters"
	@echo "  make format     - Auto-format code"
	@echo "  make run        - Run the application"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run - Run Docker container"
	@echo "  make clean      - Clean temporary files and caches"
	@echo "  make all        - Run all tasks sequentially (lint -> format -> test)"

# Setup development environment
setup:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@if [ ! -f mcp-grafana ]; then \
		echo "Downloading mcp-grafana binary..."; \
		curl -L -o mcp-grafana https://github.com/langchain-ai/langchain-mcp/releases/download/v0.0.1/mcp-grafana-linux-amd64; \
		chmod +x mcp-grafana; \
	fi

# Run tests
test:
	$(PYTEST) tests/ -v

# Check code with linters
lint:
	$(FLAKE8) app/ tests/
	$(MYPY) app/ tests/
	$(ISORT) --check app/ tests/
	$(BLACK) --check app/ tests/

# Auto-format code
format:
	$(ISORT) app/ tests/
	$(BLACK) app/ tests/

# Run the application
run:
	$(PYTHON) main.py

# Build Docker image
docker-build:
	$(DOCKER) build -t grafanallm-alertanalyzer .

# Run Docker container
docker-run:
	$(DOCKER) run -p 8000:8000 --env-file .env grafanallm-alertanalyzer

# Clean temporary files and caches
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Run all tasks sequentially
all: lint format test