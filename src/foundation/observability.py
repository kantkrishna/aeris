# src/foundation/observability.py
"""
Pipeline Observability Telemetry.

Captures and records execution metadata (SLIs) for pipeline runs into an
audit log, supporting operational dashboards.

Exported Classes:
    TelemetryLogger: Handles concurrent audit logging and metrics.
"""

import sqlite3
from typing import Optional, Dict
from datetime import datetime


class TelemetryLogger:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._init_schema()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS ops_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    job_name TEXT,
                    status TEXT,
                    rows_processed INTEGER,
                    error_msg TEXT
                )
            """)

    def log_run(
        self,
        job_name: str,
        status: str,
        rows_processed: int = 0,
        error_msg: Optional[str] = None,
    ) -> None:
        # Use isolation_level for thread concurrency in shared memory mock
        with self.conn:
            self.conn.execute(
                "INSERT INTO ops_audit_log (timestamp, job_name, status, rows_processed, error_msg) VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(),
                    job_name,
                    status,
                    rows_processed,
                    error_msg,
                ),
            )

    def get_dashboard_metrics(self) -> Dict[str, float]:
        cursor = self.conn.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM ops_audit_log").fetchone()[0]
        successes = cursor.execute(
            "SELECT COUNT(*) FROM ops_audit_log WHERE status='SUCCESS'"
        ).fetchone()[0]

        rate = (successes / total * 100) if total > 0 else 0.0
        return {"success_rate": rate, "total_runs": float(total)}
