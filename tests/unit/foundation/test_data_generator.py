# tests/unit/foundation/test_data_generator.py
"""
Synthetic Data Generation Engine Tests.

This module contains unit tests for the logistics synthetic data generator.
It ensures that referential integrity (PK/FK) is maintained across generated
entities and that business rules (e.g., delivery date after ship date) are respected.
"""

import csv
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
from typing import Generator

# These will fail until Phase 2 is implemented
from src.foundation.data_generator import generate_logistics_data


@pytest.fixture
def output_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture providing a temporary directory for output files."""
    yield tmp_path


def test_generate_data_creates_files(output_dir: Path) -> None:
    """Test that all 4 required entity files are created with data."""
    generate_logistics_data(str(output_dir), num_customers=5, num_orders=10)

    for entity in ["customers", "carriers", "orders", "shipments"]:
        file_path = output_dir / f"{entity}.csv"
        assert file_path.exists(), f"{entity}.csv was not created."

        with open(file_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            assert len(reader) > 1, f"{entity}.csv should have headers and data."


def test_delivery_date_after_ship_date(output_dir: Path) -> None:
    """Test that delivery_date is strictly after ship_date in shipments."""
    generate_logistics_data(str(output_dir), num_customers=1, num_orders=5)

    with open(output_dir / "shipments.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ship_date = datetime.fromisoformat(row["ship_date"])
            if row["delivery_date"]:  # Some might be in transit (empty)
                delivery_date = datetime.fromisoformat(row["delivery_date"])
                assert delivery_date >= ship_date, "Delivery date must be >= ship date."


def test_referential_integrity(output_dir: Path) -> None:
    """Test that orders reference valid customers (FK integrity)."""
    generate_logistics_data(str(output_dir), num_customers=5, num_orders=20)

    customers = set()
    with open(output_dir / "customers.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers.add(row["customer_id"])

    with open(output_dir / "orders.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assert row["customer_id"] in customers, "Order references invalid customer."


def test_empty_batch(output_dir: Path) -> None:
    """Test that generating 0 records does not crash and produces empty headers."""
    generate_logistics_data(str(output_dir), num_customers=0, num_orders=0)

    with open(output_dir / "orders.csv", "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 1, "Should only contain headers."


def test_permission_error(output_dir: Path) -> None:
    """Test that file write permission issues raise PermissionError cleanly."""
    with patch("builtins.open", side_effect=PermissionError("Access denied")):
        with pytest.raises(PermissionError):
            generate_logistics_data(str(output_dir), num_customers=1, num_orders=1)
