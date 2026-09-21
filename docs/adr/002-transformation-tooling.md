# ADR 002: Transformation Tooling
## Context
We need to apply modular transformations (Raw -> Staging -> Curated).
## Decision
We will use dbt (data build tool) for SQL-based transformations.
## Consequences
Enables TDD on data logic, automated quality testing, and version control.
