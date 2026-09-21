# ADR 001: Data Engine Selection
## Context
We need a highly scalable, SQL-compliant data engine for AERIS V1.
## Decision
We will use Snowflake as the primary data engine.
## Consequences
Allows decoupled compute/storage and native RBAC, but locks us into a specific vendor ecosystem for V1.
