.PHONY: venv install lint test setup clean all

venv:
	uv venv

install: venv
	uv pip install -e ".[dev]"

lint:
	uv run mypy src/foundation/repo_linter.py tests/unit/foundation/test_repo_linter.py --strict

test:
	uv run pytest tests/unit/foundation/test_repo_linter.py --cov=src.foundation.repo_linter --cov-report=term-missing

setup:
	uv run python scripts/setup_skeleton.py

clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +

all: install lint test setup