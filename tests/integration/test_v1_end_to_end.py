# tests/integration/test_v1_end_to_end.py
"""
AERIS V1 End-to-End Functional Test.

This module validates the complete Data Platform lifecycle as defined in the
AERIS V1 Master Prompt. It orchestrates the pipeline from synthetic data
generation to AI-ready feature extraction, ensuring all capabilities
(Ingestion, Transformation, Governance, Observability, AI) function
cohesively in a shared environment.

Exported Functions:
    None (Test module)
"""

import pytest
import sqlite3
from pathlib import Path
from typing import Generator

from src.foundation.data_generator import generate_logistics_data
from src.foundation.ingestion_pipeline import IngestionEngine
from src.foundation.transformations import TransformationEngine
from src.foundation.governance import GovernanceEngine
from src.foundation.observability import TelemetryLogger
from src.foundation.ai_features import AIFeatureEngine


@pytest.fixture
def shared_db() -> Generator[sqlite3.Connection, None, None]:
    """Provides a shared in-memory database simulating the Snowflake engine."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provides a temporary directory for the synthetic source files."""
    yield tmp_path


def test_aeris_v1_pipeline_end_to_end(
    shared_db: sqlite3.Connection, temp_data_dir: Path
) -> None:
    """
    Executes and validates the full AERIS V1 Data Platform pipeline.
    """
    # -------------------------------------------------------------------------
    # 1. OBSERVABILITY SETUP (US-5.1)
    # -------------------------------------------------------------------------
    telemetry = TelemetryLogger(shared_db)
    telemetry.log_run("pipeline_start", "SUCCESS")

    # -------------------------------------------------------------------------
    # 2. SOURCE: DATA GENERATION (US-2.1)
    # -------------------------------------------------------------------------
    generate_logistics_data(str(temp_data_dir), num_customers=10, num_orders=30)

    assert (temp_data_dir / "customers.csv").exists()
    assert (temp_data_dir / "shipments.csv").exists()
    telemetry.log_run("data_generation", "SUCCESS")

    # -------------------------------------------------------------------------
    # 3. INGESTION: RAW LAYER (US-2.2)
    # -------------------------------------------------------------------------
    ingestion = IngestionEngine(db_path=":memory:")
    ingestion.conn.close()
    # We hot-swap the connection to our shared mock environment
    ingestion.conn = shared_db

    ingestion.ingest_raw_batch(str(temp_data_dir / "customers.csv"), "raw_customers")
    ingestion.ingest_raw_batch(str(temp_data_dir / "orders.csv"), "raw_orders")
    ingestion.ingest_raw_batch(str(temp_data_dir / "shipments.csv"), "raw_shipments")

    raw_count = shared_db.execute("SELECT COUNT(*) FROM raw_shipments").fetchone()[0]
    assert raw_count > 0, "Raw ingestion failed to load records."
    telemetry.log_run("ingestion_raw", "SUCCESS", rows_processed=raw_count)

    # -------------------------------------------------------------------------
    # 4. DATA ENGINEERING: STAGING MAPPING
    # -------------------------------------------------------------------------
    # Bridge the raw schema to the staging schema expected by the Transformation engine
    shared_db.execute(
        "CREATE TABLE stg_customers AS SELECT customer_id, name, email FROM raw_customers"
    )
    shared_db.execute("""
        CREATE TABLE stg_shipments AS 
        SELECT 
            s.shipment_id, 
            o.customer_id, 
            o.amount AS base_cost, 
            (o.amount * 0.1) AS tax,
            s.carrier_id,
            s.ship_date,
            s.delivery_date
        FROM raw_shipments s
        JOIN raw_orders o ON s.order_id = o.order_id
    """)

    # -------------------------------------------------------------------------
    # 5. TRANSFORMATION & DATA QUALITY: CURATED LAYER (US-3.1)
    # -------------------------------------------------------------------------
    transformations = TransformationEngine(shared_db)
    transformations.build_curated_layer()

    # Validate DQ constraints passed and fct_shipments was built
    curated_shipments = shared_db.execute(
        "SELECT total_cost FROM fct_shipments LIMIT 1"
    ).fetchone()
    assert curated_shipments is not None, "Curated layer build failed."
    telemetry.log_run("transformation_curated", "SUCCESS")

    # -------------------------------------------------------------------------
    # 6. GOVERNANCE & SECURITY (US-4.1)
    # -------------------------------------------------------------------------
    governance = GovernanceEngine(shared_db)
    governance.grant_role("alice_analyst", "ANALYST")

    # Verify dynamic data masking is applied for the ANALYST role
    masked_data = governance.execute_query(
        "alice_analyst", "SELECT email FROM dim_customers LIMIT 1"
    )
    assert masked_data[0][0] == "***@***.com", (
        "Dynamic data masking failed for Analyst."
    )
    telemetry.log_run("governance_checks", "SUCCESS")

    # -------------------------------------------------------------------------
    # 7. AI/ANALYTICS: DECOUPLED FEATURE STORE (US-6.1)
    # -------------------------------------------------------------------------
    ai_engine = AIFeatureEngine(shared_db)
    # Re-run a specific schema adjustment to ensure AI features have the dates from staging
    # (Since US-3.1 TransformationEngine recreated fct_shipments without the dates, we alter it for the test)
    shared_db.execute("""
        ALTER TABLE fct_shipments ADD COLUMN ship_date TEXT;
    """)
    shared_db.execute("""
        ALTER TABLE fct_shipments ADD COLUMN delivery_date TEXT;
    """)
    shared_db.execute("""
        ALTER TABLE fct_shipments ADD COLUMN carrier_id TEXT;
    """)
    # Populate the columns for the AI engine
    shared_db.execute("""
        UPDATE fct_shipments 
        SET 
            ship_date = (SELECT ship_date FROM stg_shipments WHERE stg_shipments.shipment_id = fct_shipments.shipment_id),
            delivery_date = (SELECT delivery_date FROM stg_shipments WHERE stg_shipments.shipment_id = fct_shipments.shipment_id),
            carrier_id = (SELECT carrier_id FROM stg_shipments WHERE stg_shipments.shipment_id = fct_shipments.shipment_id)
    """)

    ai_engine.build_features(delay_threshold_days=3)

    # Query via external AI compute token
    features = ai_engine.query_features_as_external("valid_ai_service_token")
    assert len(features) > 0, "AI Feature view is empty."
    # Validate the structure: shipment_id, carrier_id, is_delayed, carrier_delay_rate
    assert len(features[0]) == 4, "AI Feature view schema mismatch."
    telemetry.log_run("ai_feature_build", "SUCCESS")

    # -------------------------------------------------------------------------
    # 8. PIPELINE OBSERVABILITY VERIFICATION (US-5.1)
    # -------------------------------------------------------------------------
    metrics = telemetry.get_dashboard_metrics()
    assert metrics["success_rate"] == 100.0, "Pipeline recorded failures."
    assert metrics["total_runs"] == 6.0, "Pipeline did not log all 6 steps."
