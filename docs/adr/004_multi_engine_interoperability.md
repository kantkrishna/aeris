# docs/adr/004_multi_engine_interoperability.md
<!-- US-18.1 Architecture Decision Record -->
# ADR 004: Multi-Engine Interoperability

## Status
Accepted

## Context
AERIS is integrating Databricks alongside Snowflake. Data duplication must be minimized.

## Decision
We will use cloud-native object storage (S3/ADLS) with open table formats (Delta/Iceberg). Cross-engine access will utilize External Tables/Federation logic over physical data movement.

## Consequences
Reduces storage cost and pipeline latency. Increases IAM governance complexity due to managing cross-cloud storage policies instead of internal engine RBAC.