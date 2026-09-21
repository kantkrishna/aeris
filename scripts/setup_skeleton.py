# scripts/setup_skeleton.py
"""
AERIS Repository Skeleton Initialization Script.

This module automates the creation of the AERIS V1 directory tree and generates
the foundational Architecture Decision Records (ADRs) to satisfy Epic 1 requirements.

Exported Functions:
    create_skeleton(base_path): Creates directories and ADR files.

Module Attributes:
    REQUIRED_DIRS (list[str]): Core directories for the platform.
"""

import os
from pathlib import Path

REQUIRED_DIRS = [
    "infrastructure",
    "transformations",
    "ingestion",
    "docs/adr",
    "src/foundation",
    "tests/unit/foundation"
]

ADR_001 = """# ADR 001: Data Engine Selection
## Context
We need a highly scalable, SQL-compliant data engine for AERIS V1.
## Decision
We will use Snowflake as the primary data engine.
## Consequences
Allows decoupled compute/storage and native RBAC, but locks us into a specific vendor ecosystem for V1.
"""

ADR_002 = """# ADR 002: Transformation Tooling
## Context
We need to apply modular transformations (Raw -> Staging -> Curated).
## Decision
We will use dbt (data build tool) for SQL-based transformations.
## Consequences
Enables TDD on data logic, automated quality testing, and version control.
"""

ADR_003 = """# ADR 003: Repository Structure
## Context
AERIS platform code must separate infrastructure, ingestion, and transformation logic.
## Decision
We will use a monolithic repository with top-level capability folders (`infrastructure`, `ingestion`, `transformations`, `docs`).
## Consequences
Simplifies CI/CD and dependency management for V1 without the complexity of micro-repos.
"""

def create_skeleton(base_path: Path) -> None:
    """Creates the standard directories and ADR files."""
    for directory in REQUIRED_DIRS:
        (base_path / directory).mkdir(parents=True, exist_ok=True)
    
    # Write foundational ADRs
    adr_path = base_path / "docs" / "adr"
    (adr_path / "001-data-engine.md").write_text(ADR_001)
    (adr_path / "002-transformation-tooling.md").write_text(ADR_002)
    (adr_path / "003-repo-structure.md").write_text(ADR_003)
    
    print("AERIS skeleton initialized successfully.")

if __name__ == "__main__":
    create_skeleton(Path.cwd())