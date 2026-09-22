# tests/unit/foundation/test_ai_features.py
"""
AI-Ready Data Product Tests.

Validates the generation of the decoupled AI feature view for Shipment Delay
Intelligence, ensuring data completeness and security for external compute.
"""

import pytest
import sqlite3
from typing import Generator

# These imports will fail until Phase 2 is implemented
from src.foundation.ai_features import AIFeatureEngine


@pytest.fixture
def ai_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    # Mock curated data
    conn.execute(
        "CREATE TABLE fct_shipments (shipment_id TEXT, carrier_id TEXT, ship_date TEXT, delivery_date TEXT)"
    )
    conn.execute(
        "INSERT INTO fct_shipments VALUES ('S1', 'CAR1', '2023-01-01', '2023-01-05')"
    )  # 4 days
    conn.execute(
        "INSERT INTO fct_shipments VALUES ('S2', 'CAR1', '2023-01-02', '2023-01-12')"
    )  # 10 days (Delayed)
    yield conn
    conn.close()


def test_delay_feature_no_nulls(ai_db: sqlite3.Connection) -> None:
    """Test that ai_shipment_features calculates delay flag with 0% nulls."""
    engine = AIFeatureEngine(ai_db)
    engine.build_features(delay_threshold_days=5)

    rows = ai_db.execute("SELECT is_delayed FROM ai_shipment_features").fetchall()
    assert len(rows) == 2
    assert all(r[0] is not None for r in rows), "Target variable contains nulls"
    assert rows[0][0] == 0  # 4 days < 5
    assert rows[1][0] == 1  # 10 days > 5


def test_carrier_delay_avg(ai_db: sqlite3.Connection) -> None:
    """Test carrier delay avg calculates correctly even for small sample sizes."""
    engine = AIFeatureEngine(ai_db)
    engine.build_features(delay_threshold_days=5)

    # CAR1 has 2 shipments, 1 delayed. Avg should be 0.5
    avg = ai_db.execute(
        "SELECT carrier_delay_rate FROM ai_shipment_features WHERE carrier_id = 'CAR1'"
    ).fetchone()[0]
    assert avg == 0.5


def test_unauthorized_ai_compute(ai_db: sqlite3.Connection) -> None:
    """Test that unauthorized external connections are denied."""
    engine = AIFeatureEngine(ai_db)
    engine.build_features()

    with pytest.raises(PermissionError, match="Unauthorized"):
        engine.query_features_as_external("invalid_token")
