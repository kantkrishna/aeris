# src/foundation/ai_features.py
"""
AI Feature Store Builder.

Transforms governed, curated data into a denormalized feature view optimized
for machine learning model training, ensuring engine decoupling.

Exported Classes:
    AIFeatureEngine: Builds and serves the shipment delay feature view.
"""

import sqlite3
from typing import List, Any


class AIFeatureEngine:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def build_features(self, delay_threshold_days: int = 5) -> None:
        """Denormalizes data and calculates the `is_delayed` label and carrier features."""
        with self.conn:
            self.conn.execute("DROP TABLE IF EXISTS ai_shipment_features")
            # SQLite specific mock logic for date differences (using julianday)
            self.conn.execute(f"""
                CREATE TABLE ai_shipment_features AS 
                WITH Base AS (
                    SELECT 
                        shipment_id,
                        carrier_id,
                        CASE 
                            WHEN (julianday(delivery_date) - julianday(ship_date)) > {delay_threshold_days} THEN 1 
                            ELSE 0 
                        END as is_delayed
                    FROM fct_shipments
                ),
                CarrierStats AS (
                    SELECT carrier_id, AVG(is_delayed) as carrier_delay_rate
                    FROM Base GROUP BY carrier_id
                )
                SELECT b.shipment_id, b.carrier_id, b.is_delayed, c.carrier_delay_rate
                FROM Base b
                JOIN CarrierStats c ON b.carrier_id = c.carrier_id
            """)

    def query_features_as_external(self, token: str) -> List[Any]:
        """Simulates external application authentication."""
        if token != "valid_ai_service_token":
            raise PermissionError("Unauthorized AI compute connection.")

        return self.conn.execute("SELECT * FROM ai_shipment_features").fetchall()
