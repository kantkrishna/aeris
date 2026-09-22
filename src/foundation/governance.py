# src/foundation/governance.py
"""
Governance and Role-Based Access Engine.

Simulates Snowflake's native RBAC and dynamic data masking capabilities,
ensuring sensitive PII is masked dynamically based on the querying user's role.

Exported Classes:
    GovernanceEngine: Manages roles and proxies queries.
    InsufficientPrivilegesError: Raised for unauthorized DB actions.
"""

import sqlite3
from typing import Dict, Any, List


class InsufficientPrivilegesError(Exception):
    pass


class GovernanceEngine:
    VALID_ROLES = ["DATA_SCIENTIST", "ANALYST", "SYSADMIN"]

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.user_roles: Dict[str, str] = {}

    def grant_role(self, username: str, role: str) -> None:
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {role}")
        self.user_roles[username] = role

    def execute_query(self, username: str, query: str) -> List[Any]:
        role = self.user_roles.get(username, "PUBLIC")

        if "DROP" in query.upper() and role != "SYSADMIN":
            raise InsufficientPrivilegesError(f"Role {role} cannot drop tables.")

        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        # Simulate Dynamic Data Masking on email columns for ANALYST
        if role == "ANALYST" and "email" in query.lower():
            # In SQLite mock, we assume column 0 is email for simplicity if selected alone
            rows = [("***@***.com", *r[1:]) for r in rows]

        return rows
