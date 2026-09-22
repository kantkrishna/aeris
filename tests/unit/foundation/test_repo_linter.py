# tests/unit/foundation/test_repo_linter.py
"""
Repository Structure and ADR Linter Tests.

This module contains unit tests for the repository structural linter, ensuring
that the required directories for the AERIS platform exist and that all
Architectural Decision Records (ADRs) adhere to the required Markdown template.
"""

import pytest
from pathlib import Path
from typing import Generator

# Note: In the RED phase, this import will fail until Phase 2 is implemented.
from src.foundation.repo_linter import get_missing_directories, validate_adr_format


@pytest.fixture
def temp_repo_structure(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture to create a temporary directory for testing filesystem operations."""
    yield tmp_path


def test_get_missing_directories_all_present(temp_repo_structure: Path) -> None:
    """Test that no directories are reported missing when all exist."""
    required = ["infrastructure", "transformations", "ingestion", "docs/adr"]
    for req in required:
        (temp_repo_structure / req).mkdir(parents=True)

    missing = get_missing_directories(temp_repo_structure, required)
    assert not missing, f"Expected empty list, got {missing}"


def test_get_missing_directories_some_missing(temp_repo_structure: Path) -> None:
    """Test that missing directories are correctly identified."""
    required = ["infrastructure", "docs/adr", "src"]
    (temp_repo_structure / "src").mkdir()

    missing = get_missing_directories(temp_repo_structure, required)
    assert missing == ["infrastructure", "docs/adr"]


def test_validate_adr_format_valid() -> None:
    """Test that a valid ADR markdown string passes validation."""
    valid_adr = (
        "# ADR 001: Data Engine Selection\n"
        "## Context\nWe need a data engine.\n"
        "## Decision\nWe selected Snowflake."
    )
    assert validate_adr_format(valid_adr) is True


def test_validate_adr_format_invalid_missing_decision() -> None:
    """Test that an ADR missing the 'Decision' section fails validation."""
    invalid_adr = (
        "# ADR 002: Transformation Tooling\n"
        "## Context\nWe need a transformation tool.\n"
        "## Alternatives Considered\ndbt, Dataform."
    )
    assert validate_adr_format(invalid_adr) is False


def test_validate_adr_format_invalid_missing_title() -> None:
    """Test that an ADR missing the primary title fails validation."""
    invalid_adr = "## Context\nSome context.\n## Decision\nSome decision."
    assert validate_adr_format(invalid_adr) is False
