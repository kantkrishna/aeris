# aeris
AERIS (Adaptive Enterprise Reliability &amp; Intelligence System) is an extensible enterprise Data &amp; AI platform that unifies data products, governance, reliability, and AI across Snowflake, Databricks, and open data technologies enabling scalable, governed, and engine-agnostic data intelligence.

Here is the updated content for your `README.md`. It covers the core value delivered in this V1 milestone, clear execution instructions, and the steps to verify the results.

# AERIS Data Platform - V1 Foundation

Welcome to the AERIS (Adaptive Enterprise Reliability & Intelligence System) V1 Data Platform. This repository contains the foundational architecture for a production-oriented, decoupled enterprise data platform.

## 🌟 End-User Value Achieved

In this V1 milestone, we have delivered a fully functional, end-to-end data pipeline that bridges the gap between raw enterprise data and AI readiness. By decoupling platform capabilities from the underlying compute engine, we deliver distinct value across multiple data personas:

*   **For Data Engineers:** Automated, reliable batch and incremental ingestion pipelines that handle raw EL (Extract, Load) operations seamlessly.
*   **For Analytics Engineers:** Modular data transformations (Staging to Curated) with built-in, automated Data Quality (DQ) checks to guarantee downstream trust.
*   **For Governance & Security Teams:** Enforced Role-Based Access Control (RBAC) and dynamic data masking, ensuring sensitive PII is protected by default without manual intervention.
*   **For Platform Operators:** Centralized pipeline telemetry and observability, providing instant SLI metrics on pipeline health and data freshness.
*   **For Data Scientists:** A decoupled, highly curated "AI Feature Store" that provides clean, historical data (e.g., Shipment Delay Intelligence) ready for ML model training, accessible securely via external compute.

## 🚀 Running the V1 Pipeline Demo

We have included a visual demonstration script that orchestrates the entire pipeline locally—from synthetic data generation to AI feature extraction—using a lightweight SQLite backend to simulate Snowflake's compute capabilities.

### Prerequisites
Ensure you have `uv` installed and your virtual environment activated. 

1. Install the project dependencies (including `pandas` for clean terminal formatting):
   ```bash
   uv pip install -e ".[dev]"
   uv add pandas --dev
   ```
2. Execute the demo script:
    ```bash
    uv run python scripts/run_v1_demo.py
    ```

## 🔍 How to Verify What We Achieved

Running the demo script generates physical artifacts and console outputs. You can visually verify the pipeline's success in three ways:

1. **Console Output (Immediate Verification):**
* **Observability:** The terminal will print the Operations Audit Log, proving that every step of the pipeline (generation, ingestion, transformation, governance, AI build) executed successfully.
* **Governance:** You will see the results of a query executed under the `ANALYST` role, proving that dynamic data masking successfully redacted customer emails (e.g., `***@***.com`).
* **AI Readiness:** The terminal will display the top 5 rows of the `ai_shipment_features` table, showing the calculated delay labels and carrier performance metrics.

2. **Inspect the Raw Data Assets:**
* Navigate to the newly created `demo_output/data/` directory.
* You will see four generated `.csv` files (`customers.csv`, `orders.csv`, `carriers.csv`, `shipments.csv`). Opening these will verify that referential integrity (Primary/Foreign Keys) and chronological business logic (delivery dates > ship dates) were successfully generated.

3. **Query the Local Database:**
* The demo persists the simulated Data Warehouse to `demo_output/aeris_v1.db`.
* If you are using VS Code, install the **SQLite Viewer** extension.
* Click on the `.db` file in your explorer to natively browse and run SQL queries against the `raw_shipments`, `stg_shipments`, `fct_shipments`, and `ai_shipment_features` tables to verify the structural transformations step-by-step.
