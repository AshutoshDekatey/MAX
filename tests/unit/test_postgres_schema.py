from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DDL = REPO_ROOT / "source-systems" / "core-banking" / "sql" / "001_v0_source_schemas.sql"


def test_v0_ddl_declares_required_tables():
    sql = DDL.read_text(encoding="utf-8").lower()
    required = [
        "core_banking.customers",
        "core_banking.accounts",
        "core_banking.cards",
        "core_banking.addresses",
        "core_banking.customer_status_history",
        "fraud_ops.fraud_cases",
    ]
    for table in required:
        assert f"create table if not exists {table}" in sql


def test_v0_ddl_uses_foreign_keys_and_constraints():
    sql = DDL.read_text(encoding="utf-8").lower()
    assert "references core_banking.customers(customer_id)" in sql
    assert "check (" in sql
    assert "create index" in sql

