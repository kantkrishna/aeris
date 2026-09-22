# tests/unit/foundation/test_observability.py
"""
Pipeline Telemetry and SLI Dashboard Tests.

This module ensures pipeline metadata is accurately logged to the audit table
and that concurrency locking does not drop logs.
"""

import pytest
import sqlite3
import threading
from typing import Generator

# These imports will fail until Phase 2 is implemented
from src.foundation.observability import TelemetryLogger


@pytest.fixture
def telemetry_db() -> Generator[sqlite3.Connection, None, None]:
    # Use shared memory for thread testing
    conn = sqlite3.connect(
        "file::memory:?cache=shared", uri=True, check_same_thread=False
    )
    yield conn
    conn.close()


def test_success_and_failure_logging(telemetry_db: sqlite3.Connection) -> None:
    """Test logging of SUCCESS and FAILED pipeline events."""
    logger = TelemetryLogger(telemetry_db)
    logger.log_run("ingest_raw", "SUCCESS", rows_processed=100)
    logger.log_run("transform", "FAILED", error_msg="Data Quality Error")

    logs = telemetry_db.execute(
        "SELECT job_name, status, error_msg FROM ops_audit_log ORDER BY id"
    ).fetchall()
    assert logs[0] == ("ingest_raw", "SUCCESS", None)
    assert logs[1] == ("transform", "FAILED", "Data Quality Error")

    # Dashboard metrics test
    metrics = logger.get_dashboard_metrics()
    assert metrics["success_rate"] == 50.0


def test_concurrent_logging(telemetry_db: sqlite3.Connection) -> None:
    """Test that concurrent runs are captured without locking issues."""
    logger = TelemetryLogger(telemetry_db)

    def worker(i: int) -> None:
        logger.log_run(f"job_{i}", "SUCCESS", 10)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    count = telemetry_db.execute("SELECT COUNT(*) FROM ops_audit_log").fetchone()[0]
    assert count == 10
