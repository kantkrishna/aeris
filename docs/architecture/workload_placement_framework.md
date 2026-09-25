# docs/architecture/workload_placement_framework.md
<!-- US-17.1 Workload Placement Framework -->
# Workload Placement Decision Framework

## 1. Characteristics
Analyze if the workload is primarily procedural SQL, high-volume batch streaming, or ML inference.

## 2. Performance
Determine the required SLA and optimal parallelization capabilities required.

## 3. Cost
Score based on compute up-time and per-second billing requirements.

## 4. Ecosystem Requirements
Evaluate if the workload requires tight integration with specific native governance layers (e.g., Unity Catalog vs. Horizon).