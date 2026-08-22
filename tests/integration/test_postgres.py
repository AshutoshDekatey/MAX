from __future__ import annotations

import os
from datetime import datetime

import psycopg
import pytest

from project_max.config import GenerationConfig
from project_max.generation.orchestrator import generate_bank


@pytest.mark.postgres
def test_generated_core_records_load_into_disposable_postgres(tmp_path):
    database_url = os.getenv("MAX_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("MAX_TEST_DATABASE_URL is not configured")

    config = GenerationConfig(
        seed=77,
        customers=7,
        transactions=20,
        merchants=5,
        fraud_rate=0.2,
        as_of=datetime.fromisoformat("2026-08-20T12:00:00+00:00"),
    )
    generate_bank(tmp_path / "run", config, database_url=database_url)
    with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM core_banking.customers WHERE customer_id LIKE 'CUS%'")
        assert cursor.fetchone()[0] >= 7
        cursor.execute("SELECT count(*) FROM fraud_ops.fraud_cases")
        assert cursor.fetchone()[0] >= 1

