"""PostgreSQL bootstrap and load adapter for Meridian source records."""

from __future__ import annotations

import csv
from pathlib import Path

import psycopg

from project_max.generation.common import read_jsonl

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DDL_PATH = REPOSITORY_ROOT / "source-systems" / "core-banking" / "sql" / "001_v0_source_schemas.sql"


def bootstrap_database(database_url: str) -> None:
    """Create V0 schemas and tables in a database chosen by Max."""
    ddl = DDL_PATH.read_text(encoding="utf-8")
    with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute(ddl)


def _csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _upsert(cursor: psycopg.Cursor, table: str, key: str, rows: list[dict]) -> None:
    if not rows:
        return
    columns = list(rows[0])
    column_sql = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    updates = ", ".join(f"{column} = EXCLUDED.{column}" for column in columns if column != key)
    sql = (
        f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders}) "
        f"ON CONFLICT ({key}) DO UPDATE SET {updates}"
    )
    values = [[row.get(column) or None for column in columns] for row in rows]
    cursor.executemany(sql, values)


def load_generated_run(database_url: str, run_dir: Path) -> None:
    """Load clean operational records; deliberately dirty extracts remain files."""
    bootstrap_database(database_url)
    with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
        core = run_dir / "core_banking"
        _upsert(cursor, "core_banking.customers", "customer_id", _csv_rows(core / "customers.csv"))
        _upsert(cursor, "core_banking.accounts", "account_id", _csv_rows(core / "accounts.csv"))
        _upsert(cursor, "core_banking.cards", "card_id", _csv_rows(core / "cards.csv"))
        _upsert(cursor, "core_banking.addresses", "address_id", _csv_rows(core / "addresses.csv"))
        _upsert(
            cursor,
            "core_banking.customer_status_history",
            "history_id",
            _csv_rows(core / "customer_status_history.csv"),
        )
        _upsert(
            cursor,
            "fraud_ops.fraud_cases",
            "case_id",
            read_jsonl(run_dir / "fraud_cases" / "fraud_cases.jsonl"),
        )

