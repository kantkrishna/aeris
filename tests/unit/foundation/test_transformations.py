# tests/unit/foundation/test_transformations.py
"""
Transformation & Data Quality Tests.

This module contains unit tests for the transformation logic (Staging to Curated)
and the automated Data Quality (DQ) checks, ensuring business logic and schema
validity are applied reproducibly.
"""

import pytest
import sqlite3
from typing import Generator

# These imports will fail until Phase 2 is implemented
from src.foundation.transformations import TransformationEngine, DataQualityError


@pytest.fixture
def db_conn() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    # Setup mock staging data
    conn.execute(
        "CREATE TABLE stg_shipments (shipment_id TEXT, customer_id TEXT, base_cost REAL, tax REAL)"
    )
    conn.execute("CREATE TABLE stg_customers (customer_id TEXT, name TEXT, email TEXT)")
    conn.execute("INSERT INTO stg_customers VALUES ('C1', 'Alice', 'alice@test.com')")
    yield conn
    conn.close()


def test_total_cost_calculation(db_conn: sqlite3.Connection) -> None:
    """Test that fct_shipments calculates total_cost correctly."""
    db_conn.execute("INSERT INTO stg_shipments VALUES ('S1', 'C1', 10.0, 2.5)")
    engine = TransformationEngine(db_conn)

    engine.build_curated_layer()
    result = db_conn.execute(
        "SELECT total_cost FROM fct_shipments WHERE shipment_id = 'S1'"
    ).fetchone()

    assert result[0] == 12.5


def test_null_customer_id_fails_dq(db_conn: sqlite3.Connection) -> None:
    """Test that a NULL customer_id in staging triggers a Data Quality Error."""
    db_conn.execute("INSERT INTO stg_shipments VALUES ('S2', NULL, 10.0, 2.0)")
    engine = TransformationEngine(db_conn)

    with pytest.raises(
        DataQualityError, match="NULL values found in required column: customer_id"
    ):
        engine.build_curated_layer()


def test_negative_cost_fails_dq(db_conn: sqlite3.Connection) -> None:
    """Test that $0 cost is allowed, but negative cost fails DQ check."""
    db_conn.execute(
        "INSERT INTO stg_shipments VALUES ('S3', 'C1', 0.0, 0.0)"
    )  # $0 is valid
    db_conn.execute(
        "INSERT INTO stg_shipments VALUES ('S4', 'C1', -5.0, 0.0)"
    )  # Negative is invalid
    engine = TransformationEngine(db_conn)

    with pytest.raises(DataQualityError, match="Negative values found in base_cost"):
        engine.build_curated_layer()
