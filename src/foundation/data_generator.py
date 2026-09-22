# src/foundation/data_generator.py
"""
Logistics Synthetic Data Generator.

This module provides utilities to generate structurally sound synthetic logistics
data (Customers, Carriers, Orders, Shipments) for pipeline testing.

Exported Functions:
    generate_logistics_data(output_dir, num_customers, num_orders): Writes CSV files.

Module Attributes:
    None
"""

import csv
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


def generate_logistics_data(
    output_dir: str, num_customers: int = 100, num_orders: int = 500
) -> None:
    """
    Generates CSV files for logistics entities in the target directory.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Generate Carriers
    carriers: List[Dict[str, Any]] = [
        {"carrier_id": str(uuid.uuid4()), "name": f"Carrier {i}"} for i in range(5)
    ]

    # 2. Generate Customers
    customers: List[Dict[str, Any]] = [
        {
            "customer_id": str(uuid.uuid4()),
            "name": f"Customer {i}",
            "email": f"cust{i}@example.com",
        }
        for i in range(num_customers)
    ]

    # 3. Generate Orders & Shipments
    orders: List[Dict[str, Any]] = []
    shipments: List[Dict[str, Any]] = []

    start_date = datetime(2023, 1, 1)

    for i in range(num_orders):
        if not customers:
            break

        cust = random.choice(customers)
        order_id = str(uuid.uuid4())
        order_date = start_date + timedelta(days=random.randint(0, 365))

        orders.append(
            {
                "order_id": order_id,
                "customer_id": cust["customer_id"],
                "order_date": order_date.isoformat(),
                "amount": round(random.uniform(10.0, 1000.0), 2),
            }
        )

        # 1-to-1 Shipment for simplicity
        carrier = random.choice(carriers)
        ship_date = order_date + timedelta(days=random.randint(1, 3))
        delivery_date = ship_date + timedelta(days=random.randint(1, 7))

        shipments.append(
            {
                "shipment_id": str(uuid.uuid4()),
                "order_id": order_id,
                "carrier_id": carrier["carrier_id"],
                "ship_date": ship_date.isoformat(),
                "delivery_date": delivery_date.isoformat(),
                "status": "DELIVERED",
            }
        )

    # Write Files
    _write_csv(out_path / "carriers.csv", ["carrier_id", "name"], carriers)
    _write_csv(out_path / "customers.csv", ["customer_id", "name", "email"], customers)
    _write_csv(
        out_path / "orders.csv",
        ["order_id", "customer_id", "order_date", "amount"],
        orders,
    )
    _write_csv(
        out_path / "shipments.csv",
        [
            "shipment_id",
            "order_id",
            "carrier_id",
            "ship_date",
            "delivery_date",
            "status",
        ],
        shipments,
    )


def _write_csv(file_path: Path, headers: List[str], data: List[Dict[str, Any]]) -> None:
    """Helper to write dictionaries to CSV."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
