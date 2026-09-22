# tests/unit/foundation/test_governance.py
"""
Governance and Role-Based Access Control Tests.

This module validates that RBAC policies and dynamic data masking rules are
applied correctly based on user roles, simulating Snowflake governance.
"""

import pytest
import sqlite3
from typing import Generator

# These imports will fail until Phase 2 is implemented
from src.foundation.governance import GovernanceEngine, InsufficientPrivilegesError


@pytest.fixture
def gov_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE dim_customers (customer_id TEXT, email TEXT)")
    conn.execute("INSERT INTO dim_customers VALUES ('C1', 'secret@enterprise.com')")
    yield conn
    conn.close()


def test_data_scientist_read(gov_db: sqlite3.Connection) -> None:
    """Test that DATA_SCIENTIST can read unmasked data."""
    engine = GovernanceEngine(gov_db)
    engine.grant_role("ds_user", "DATA_SCIENTIST")

    rows = engine.execute_query("ds_user", "SELECT email FROM dim_customers")
    assert rows[0][0] == "secret@enterprise.com"


def test_analyst_dynamic_masking(gov_db: sqlite3.Connection) -> None:
    """Test that ANALYST role sees dynamically masked email addresses."""
    engine = GovernanceEngine(gov_db)
    engine.grant_role("analyst_user", "ANALYST")

    rows = engine.execute_query("analyst_user", "SELECT email FROM dim_customers")
    assert rows[0][0] == "***@***.com"


def test_insufficient_privileges(gov_db: sqlite3.Connection) -> None:
    """Test that ANALYST cannot drop tables."""
    engine = GovernanceEngine(gov_db)
    engine.grant_role("analyst_user", "ANALYST")

    with pytest.raises(InsufficientPrivilegesError):
        engine.execute_query("analyst_user", "DROP TABLE dim_customers")


def test_invalid_role(gov_db: sqlite3.Connection) -> None:
    """Test that assigning an invalid role fails cleanly."""
    engine = GovernanceEngine(gov_db)
    with pytest.raises(ValueError, match="Invalid role"):
        engine.grant_role("bad_user", "SUPER_ADMIN")
