# Goal

Evolve AERIS V1 into a production-oriented platform demonstrating **reliability, security, delivery automation and platform economics**.

Preserve existing architecture unless evidence indicates a change is required.

Work iteratively: **explore → implement → execute → inject failure → diagnose → improve → validate**.

# Epics

## E1 — Reliable Data Processing

**Deliverables**

* Add CDC-style/incremental processing.
* Handle duplicates, late data and schema changes.
* Implement retry, idempotency and replay.
* Add representative failure scenarios.

**Expected outcome:** Pipelines can recover from realistic operational failures without corrupting data.

## E2 — SRE & Observability

**Deliverables**

* Establish meaningful SLIs/SLOs and error budgets.
* Add pipeline and data-product health metrics.
* Demonstrate failure detection, diagnosis and recovery.
* Define operational runbooks.

**Expected outcome:** AERIS can be operated as a production platform rather than simply executed as a pipeline.

## E3 — DevSecOps

**Deliverables**

* Implement CI validation.
* Automate unit/data/integration tests.
* Add linting and basic security checks.
* Establish environment promotion and rollback.

**Expected outcome:** Platform changes follow a repeatable engineering delivery process.

## E4 — Security & Governance

**Deliverables**

* Strengthen RBAC and least privilege.
* Add masking/access policies for sensitive data.
* Add audit controls.
* Document governance responsibilities.

**Expected outcome:** Security and governance become enforceable platform capabilities.

## E5 — FinOps

**Deliverables**

* Track workload/resource consumption.
* Create workload cost attribution.
* Identify inefficient workloads.
* Perform at least one optimization experiment.

**Expected outcome:** Engineering decisions can be evaluated in terms of reliability, performance and cost.

## E6 — Engineering Operating Model

**Deliverables**

* Define platform ownership.
* Create team boundaries and responsibilities.
* Define engineering KPIs.
* Create a short roadmap and risk register.

**Expected outcome:** AERIS demonstrates how an engineering leader would organize and operate the platform.

# Definition of Done

Demonstrate:

**Change → CI/CD → Deployment → Data Processing → Failure → Detection → Recovery → Cost/Health Measurement**

Document the lessons learned and address the most significant production-readiness gaps.
