.PHONY: help install lint format test test-verbose test-coverage clean pre-commit-install pre-commit-run all check

# Default target
help:
	@echo "Available targets:"
	@echo "  make install              - Install dependencies using Poetry"
	@echo "  make lint                 - Run linter (ruff check)"
	@echo "  make format               - Format code (ruff format)"
	@echo "  make format-check         - Check code formatting without making changes"
	@echo "  make test                 - Run tests"
	@echo "  make test-verbose         - Run tests with verbose output"
	@echo "  make test-coverage        - Run tests with coverage report"
	@echo "  make clean                - Clean build artifacts and cache"
	@echo "  make pre-commit-install   - Install pre-commit hooks"
	@echo "  make pre-commit-run       - Run pre-commit on all files"
	@echo "  make check                - Run lint and test (quick check)"
	@echo "  make all                  - Run format, lint, and test (full check)"

# Install dependencies
install:
	poetry install

# Lint code
lint:
	poetry run ruff check .

# Format code
format:
	poetry run ruff format .

# Check formatting without making changes
format-check:
	poetry run ruff format --check .

# Run tests
test:
	poetry run pytest tests/ -v

# Run tests with verbose output
test-verbose:
	poetry run pytest tests/ -vv

# Run tests with coverage
test-coverage:
	poetry run pytest tests/ --cov=fastpdf4llm --cov-report=html --cov-report=term

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

# Install pre-commit hooks
pre-commit-install:
	poetry run pre-commit install

# Run pre-commit on all files
pre-commit-run:
	poetry run pre-commit run --all-files

# Quick check: lint and test
check: lint test

# Full check: format, lint, and test
all: format lint test

