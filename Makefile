.PHONY: setup test lint format run docker-build docker-run clean all help

PYTHON = python
PIP = pip
PYTEST = pytest
FLAKE8 = flake8
BLACK = black
ISORT = isort
MYPY = mypy
DOCKER = docker

# 기본 명령어
help:
	@echo "사용 가능한 명령어:"
	@echo "  make setup      - 개발 환경 설정 및 의존성 설치"
	@echo "  make test       - 테스트 실행"
	@echo "  make lint       - 코드 린트 검사"
	@echo "  make format     - 코드 자동 포맷팅"
	@echo "  make run        - 애플리케이션 실행"
	@echo "  make docker-build - Docker 이미지 빌드"
	@echo "  make docker-run - Docker 컨테이너 실행"
	@echo "  make clean      - 임시 파일 및 캐시 정리"
	@echo "  make all        - 모든 작업 순차 실행 (lint -> format -> test)"

# 개발 환경 설정
setup:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@if [ ! -f mcp-grafana ]; then \
		echo "mcp-grafana 바이너리 다운로드 중..."; \
		curl -L -o mcp-grafana https://github.com/langchain-ai/langchain-mcp/releases/download/v0.0.1/mcp-grafana-linux-amd64; \
		chmod +x mcp-grafana; \
	fi

# 테스트 실행
test:
	$(PYTEST) tests/ -v

# 코드 린트 검사
lint:
	$(FLAKE8) app/ tests/
	$(MYPY) app/ tests/
	$(ISORT) --check app/ tests/
	$(BLACK) --check app/ tests/

# 코드 자동 포맷팅
format:
	$(ISORT) app/ tests/
	$(BLACK) app/ tests/

# 애플리케이션 실행
run:
	$(PYTHON) main.py

# Docker 이미지 빌드
docker-build:
	$(DOCKER) build -t alert-analyzer .

# Docker 컨테이너 실행
docker-run:
	$(DOCKER) run -p 8000:8000 --env-file .env alert-analyzer

# 임시 파일 및 캐시 정리
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# 모든 작업 순차 실행
all: lint format test