# ADR 003: Repository Structure
## Context
AERIS platform code must separate infrastructure, ingestion, and transformation logic.
## Decision
We will use a monolithic repository with top-level capability folders (`infrastructure`, `ingestion`, `transformations`, `docs`).
## Consequences
Simplifies CI/CD and dependency management for V1 without the complexity of micro-repos.
