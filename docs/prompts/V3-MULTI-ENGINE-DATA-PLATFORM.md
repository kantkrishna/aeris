# Goal

Extend AERIS into an **engine-agnostic enterprise data platform** supporting both **Snowflake and Databricks**.

The objective is not to duplicate the same workload on two platforms. Demonstrate architectural interoperability and explain why a workload belongs on one engine or the other.

# Epics

## Epic 13 — Engine Abstraction

**Deliverables**

* Define AERIS interfaces between platform capabilities and data engines.
* Separate orchestration, governance, observability and data-product definitions from engine-specific execution.
* Create an engine capability matrix.

**Expected outcome:** AERIS can add another execution engine without redesigning the entire platform.

## Epic 14 — Databricks Integration

**Deliverables**

* Introduce Databricks as a second execution engine.
* Implement one meaningful workload using Databricks/Spark.
* Keep the existing Snowflake workload operational.

**Expected outcome:** AERIS demonstrates genuine multi-engine capability rather than merely documenting it.

## Epic 15 — Interoperability

**Deliverables**

* Define how Snowflake and Databricks exchange/access data.
* Evaluate appropriate approaches such as shared/open formats or federation.
* Document latency, cost, governance and operational trade-offs.

**Expected outcome:** A defensible architecture for cross-engine data consumption.

## Epic 16 — Unified Governance & Observability

**Deliverables**

* Provide a common AERIS metadata model.
* Track ownership, quality and lineage across engines.
* Expose unified health metrics.

**Expected outcome:** Platform governance and observability remain consistent even when workloads use different engines.

## Epic 17 — Workload Placement

**Deliverables**
Create a decision framework covering:

* workload characteristics
* performance
* scalability
* cost
* data locality
* ecosystem requirements
* operational complexity

Use it to justify where selected workloads execute.

**Expected outcome:** Engine selection becomes an engineering decision rather than a technology preference.

## Epic 18 — Architecture Review

**Deliverables**
Create ADRs covering:

* multi-engine architecture
* Snowflake vs Databricks workload placement
* interoperability
* governance
* operational ownership

**Expected outcome:** AERIS demonstrates platform-level architectural decision making.

# Definition of Done

Demonstrate:

**One AERIS Platform → Two Data Engines → Shared Governance → Shared Observability → Explicit Workload Placement**

The platform must continue to work when either engine-specific workload is modified independently.
