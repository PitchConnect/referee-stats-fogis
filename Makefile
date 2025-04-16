.PHONY: help install dev-install lint format test clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install the package"
	@echo "  make dev-install  - Install the package in development mode with dev dependencies"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up build artifacts"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

lint:
	flake8 referee_stats_fogis tests
	mypy referee_stats_fogis
	black --check referee_stats_fogis tests
	isort --check referee_stats_fogis tests

format:
	black referee_stats_fogis tests
	isort referee_stats_fogis tests

test:
	pytest

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
