# scripts/run_v1_demo.py
"""
AERIS V1 End-to-End Visual Demo.

Executes the pipeline and persists the output to local files and a local SQLite
database, printing the audit logs and final AI feature view to the console.
"""

import sys
from pathlib import Path

# Add the project root directory to Python's path so it can find 'src'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
import pandas as pd

from src.foundation.data_generator import generate_logistics_data
from src.foundation.ingestion_pipeline import IngestionEngine
from src.foundation.transformations import TransformationEngine
from src.foundation.governance import GovernanceEngine
from src.foundation.observability import TelemetryLogger
from src.foundation.ai_features import AIFeatureEngine


def main() -> None:
    # Set up physical paths for visual inspection
    output_dir = Path("demo_output/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = "demo_output/aeris_v1.db"

    # Connect to persistent local database
    shared_db = sqlite3.connect(db_path)
    print("\n🚀 Starting AERIS V1 Pipeline Demo...\n")

    # 1. Observability
    telemetry = TelemetryLogger(shared_db)
    telemetry.log_run("pipeline_start", "SUCCESS")

    # 2. Source Data Generation
    generate_logistics_data(str(output_dir), num_customers=10, num_orders=30)
    telemetry.log_run("data_generation", "SUCCESS")

    # 3. Ingestion
    ingestion = IngestionEngine(db_path=db_path)
    ingestion.ingest_raw_batch(str(output_dir / "customers.csv"), "raw_customers")
    ingestion.ingest_raw_batch(str(output_dir / "orders.csv"), "raw_orders")
    ingestion.ingest_raw_batch(str(output_dir / "shipments.csv"), "raw_shipments")
    telemetry.log_run("ingestion_raw", "SUCCESS", rows_processed=30)

    # 4. Staging Mapping (Data Engineering)
    shared_db.execute("DROP TABLE IF EXISTS stg_customers")
    shared_db.execute("DROP TABLE IF EXISTS stg_shipments")
    shared_db.execute(
        "CREATE TABLE stg_customers AS SELECT customer_id, name, email FROM raw_customers"
    )
    shared_db.execute("""
        CREATE TABLE stg_shipments AS 
        SELECT 
            s.shipment_id, o.customer_id, o.amount AS base_cost, (o.amount * 0.1) AS tax,
            s.carrier_id, s.ship_date, s.delivery_date
        FROM raw_shipments s JOIN raw_orders o ON s.order_id = o.order_id
    """)

    # 5. Transformation & DQ
    transformations = TransformationEngine(shared_db)
    transformations.build_curated_layer()
    telemetry.log_run("transformation_curated", "SUCCESS")

    # 6. Governance
    governance = GovernanceEngine(shared_db)
    governance.grant_role("alice_analyst", "ANALYST")
    telemetry.log_run("governance_checks", "SUCCESS")

    # 7. AI Features
    shared_db.execute("ALTER TABLE fct_shipments ADD COLUMN ship_date TEXT")
    shared_db.execute("ALTER TABLE fct_shipments ADD COLUMN delivery_date TEXT")
    shared_db.execute("ALTER TABLE fct_shipments ADD COLUMN carrier_id TEXT")
    shared_db.execute("""
        UPDATE fct_shipments SET 
            ship_date = (SELECT ship_date FROM stg_shipments WHERE stg_shipments.shipment_id = fct_shipments.shipment_id),
            delivery_date = (SELECT delivery_date FROM stg_shipments WHERE stg_shipments.shipment_id = fct_shipments.shipment_id),
            carrier_id = (SELECT carrier_id FROM stg_shipments WHERE stg_shipments.shipment_id = fct_shipments.shipment_id)
    """)
    ai_engine = AIFeatureEngine(shared_db)
    ai_engine.build_features(delay_threshold_days=3)
    telemetry.log_run("ai_feature_build", "SUCCESS")

    # --- VISUAL VERIFICATION OUTPUTS ---

    print("-" * 60)
    print("📊 1. OBSERVABILITY AUDIT LOG (Pipeline execution history):")
    audit_df = pd.read_sql(
        "SELECT timestamp, job_name, status, rows_processed FROM ops_audit_log",
        shared_db,
    )
    print(audit_df.to_string(index=False))

    print("\n" + "-" * 60)
    print("🔐 2. GOVERNANCE (Dynamic Data Masking for 'ANALYST' role):")
    masked_data = governance.execute_query(
        "alice_analyst", "SELECT * FROM dim_customers LIMIT 3"
    )
    for row in masked_data:
        print(row)

    print("\n" + "-" * 60)
    print("🤖 3. AI-READY DATA PRODUCT (Shipment Delay Features):")
    ai_df = pd.read_sql("SELECT * FROM ai_shipment_features LIMIT 5", shared_db)
    print(ai_df.to_string(index=False))

    print("\n" + "-" * 60)
    print(
        f"✅ Demo complete! You can inspect the physical files at:\n - Data files: {output_dir.absolute()}\n - Database: {Path(db_path).absolute()}\n"
    )


if __name__ == "__main__":
    main()
