# tests/unit/foundation/test_ingestion_pipeline.py
"""
Layered Data Ingestion Tests.

This module contains unit tests for batch (RAW) and incremental (STAGING)
ingestion pipelines, validating loading mechanisms, upsert deduplication,
and schema length constraint simulations.
"""

import csv
import pytest
from pathlib import Path
from typing import Generator

# These will fail until Phase 2 is implemented
from src.foundation.ingestion_pipeline import IngestionEngine, IngestionError


@pytest.fixture
def sample_csv(tmp_path: Path) -> Generator[Path, None, None]:
    file_path = tmp_path / "sample_customers.csv"
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "name", "email"])
        writer.writerow(["1", "Alice", "alice@example.com"])
        writer.writerow(["2", "Bob", "bob@example.com"])
    yield file_path


@pytest.fixture
def db_engine() -> Generator[IngestionEngine, None, None]:
    engine = IngestionEngine(":memory:")
    yield engine
    engine.conn.close()


def test_batch_ingestion_raw(db_engine: IngestionEngine, sample_csv: Path) -> None:
    """Test that batch ingestion loads data into RAW layer."""
    db_engine.ingest_raw_batch(str(sample_csv), "raw_customers")

    result = db_engine.conn.execute("SELECT COUNT(*) FROM raw_customers").fetchone()
    assert result[0] == 2


def test_incremental_ingestion_staging(
    db_engine: IngestionEngine, tmp_path: Path
) -> None:
    """Test that incremental ingestion merges data into STAGING without duplicates."""
    file1 = tmp_path / "inc1.csv"
    with open(file1, "w", newline="") as f:
        csv.writer(f).writerows([["id", "val"], ["1", "A"], ["2", "B"]])

    db_engine.ingest_staging_incremental(str(file1), "stg_table", ["id"])

    # Run incremental with an update to id=1 and a new row id=3
    file2 = tmp_path / "inc2.csv"
    with open(file2, "w", newline="") as f:
        csv.writer(f).writerows([["id", "val"], ["1", "A-updated"], ["3", "C"]])

    db_engine.ingest_staging_incremental(str(file2), "stg_table", ["id"])

    cursor = db_engine.conn.cursor()
    cursor.execute("SELECT id, val FROM stg_table ORDER BY id")
    rows = cursor.fetchall()

    assert len(rows) == 3
    assert rows[0] == ("1", "A-updated")  # Merged/Updated
    assert rows[1] == ("2", "B")  # Untouched
    assert rows[2] == ("3", "C")  # Inserted


def test_corrupted_file(db_engine: IngestionEngine, tmp_path: Path) -> None:
    """Test that a corrupted file fails cleanly without partial commits."""
    corrupted_file = tmp_path / "bad.csv"
    with open(corrupted_file, "w") as f:
        f.write("col1,col2\nval1\nval1,val2,val3")  # Malformed rows

    with pytest.raises(IngestionError, match="Data mismatch"):
        db_engine.ingest_raw_batch(str(corrupted_file), "raw_bad")


def test_max_string_length(db_engine: IngestionEngine, tmp_path: Path) -> None:
    """Test that exceeding max string length raises an IngestionError."""
    long_file = tmp_path / "long.csv"
    with open(long_file, "w", newline="") as f:
        csv.writer(f).writerows([["id", "name"], ["1", "A" * 300]])  # Exceeds 255

    with pytest.raises(IngestionError, match="exceeds max length"):
        db_engine.ingest_raw_batch(str(long_file), "raw_length_check", max_length=255)
