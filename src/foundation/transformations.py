# src/foundation/transformations.py
"""
Data Transformation & Quality Engine.

Executes modular SQL transformations to promote data from Staging to Curated
layers. Enforces data quality (DQ) assertions automatically.

Exported Classes:
    TransformationEngine: Handles data builds and quality tests.
    DataQualityError: Raised when DQ tests fail.
"""

import sqlite3


class DataQualityError(Exception):
    pass


class TransformationEngine:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def _run_dq_tests(self) -> None:
        """Runs automated schema and business logic validations."""
        null_customers = self.conn.execute(
            "SELECT COUNT(*) FROM stg_shipments WHERE customer_id IS NULL"
        ).fetchone()[0]
        if null_customers > 0:
            raise DataQualityError("NULL values found in required column: customer_id")

        negative_costs = self.conn.execute(
            "SELECT COUNT(*) FROM stg_shipments WHERE base_cost < 0"
        ).fetchone()[0]
        if negative_costs > 0:
            raise DataQualityError("Negative values found in base_cost")

    def build_curated_layer(self) -> None:
        """Transforms staging data into Curated products after passing DQ."""
        self._run_dq_tests()

        with self.conn:
            self.conn.execute("DROP TABLE IF EXISTS dim_customers")
            self.conn.execute(
                "CREATE TABLE dim_customers AS SELECT * FROM stg_customers"
            )

            self.conn.execute("DROP TABLE IF EXISTS fct_shipments")
            self.conn.execute("""
                CREATE TABLE fct_shipments AS 
                SELECT 
                    shipment_id, 
                    customer_id, 
                    base_cost, 
                    tax, 
                    (base_cost + tax) AS total_cost 
                FROM stg_shipments
            """)
