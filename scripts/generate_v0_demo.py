"""Generate the small, committed V0 evidence dataset."""

from datetime import datetime
from pathlib import Path

from project_max.config import GenerationConfig
from project_max.generation import generate_bank

if __name__ == "__main__":
    generate_bank(
        Path("source-systems/sample-data/v0-demo"),
        GenerationConfig(
            seed=20260820,
            customers=24,
            transactions=120,
            merchants=18,
            fraud_rate=0.10,
            as_of=datetime.fromisoformat("2026-08-20T12:00:00+00:00"),
        ),
        include_defects=True,
    )

