# src/foundation/ingestion_pipeline.py
"""
Data Ingestion Pipeline Utilities.

This module provides the core ingestion mechanisms for extracting flat files 
and loading them into relational Data Warehouse layers (RAW and STAGING). 
It simulates Snowflake's COPY INTO and MERGE behaviors using a lightweight backend.

Exported Classes:
    IngestionEngine: Handles batch append and incremental upsert operations.
    IngestionError: Custom exception for ingestion failures.

Module Attributes:
    None
"""

import csv
import sqlite3
from typing import List

class IngestionError(Exception):
    """Custom exception raised for errors during the ingestion process."""
    pass

class IngestionEngine:
    def __init__(self, db_path: str) -> None:
        """Initialize the connection to the data engine (mocked via SQLite)."""
        self.conn = sqlite3.connect(db_path)
        
    def _validate_and_read_csv(self, file_path: str, max_length: int) -> tuple[List[str], List[List[str]]]:
        """Reads CSV, validates dimensions, and checks string lengths."""
        with open(file_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            
        if not reader:
            return [], []
            
        headers = reader[0]
        data = reader[1:]
        
        for row in data:
            if len(row) != len(headers):
                raise IngestionError(f"Data mismatch: Row has {len(row)} columns, expected {len(headers)}")
            for col in row:
                if max_length and len(str(col)) > max_length:
                    raise IngestionError(f"Value '{col}' exceeds max length of {max_length}")
                    
        return headers, data

    def ingest_raw_batch(self, file_path: str, table_name: str, max_length: int = 0) -> None:
        """
        Batch ingestion: Appends all data into the RAW layer table.
        Recreates table if it does not exist.
        """
        headers, data = self._validate_and_read_csv(file_path, max_length)
        if not headers:
            return
            
        cols = ", ".join([f"{h} TEXT" for h in headers])
        placeholders = ", ".join(["?"] * len(headers))
        
        try:
            with self.conn:
                self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})")
                self.conn.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", data)
        except sqlite3.Error as e:
            raise IngestionError(f"Database error: {e}")

    def ingest_staging_incremental(self, file_path: str, table_name: str, pk_cols: List[str]) -> None:
        """
        Incremental ingestion: Merges data into the STAGING layer using Upsert logic.
        Updates existing rows and inserts new rows based on primary key(s).
        """
        headers, data = self._validate_and_read_csv(file_path, max_length=0)
        if not headers:
            return
            
        cols_def = ", ".join([f"{h} TEXT" for h in headers])
        pk_def = ", ".join(pk_cols)
        
        # Build SQLite Upsert Statement (simulating Snowflake MERGE)
        cols_str = ", ".join(headers)
        placeholders = ", ".join(["?"] * len(headers))
        updates = ", ".join([f"{h}=excluded.{h}" for h in headers if h not in pk_cols])
        
        # Edge Case: If there are no non-PK columns to update
        update_clause = f"DO UPDATE SET {updates}" if updates else "DO NOTHING"
        
        try:
            with self.conn:
                self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_def}, PRIMARY KEY ({pk_def}))")
                query = f"""
                    INSERT INTO {table_name} ({cols_str}) 
                    VALUES ({placeholders}) 
                    ON CONFLICT({pk_def}) {update_clause}
                """
                self.conn.executemany(query, data)
        except sqlite3.Error as e:
            raise IngestionError(f"Database error: {e}")