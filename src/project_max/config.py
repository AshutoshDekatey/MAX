"""Configuration primitives for the V0 simulator."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml


@dataclass(frozen=True)
class GenerationConfig:
    seed: int = 20260820
    customers: int = 100
    transactions: int = 500
    merchants: int = 50
    fraud_rate: float = 0.06
    as_of: datetime = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)

    def validate(self) -> None:
        if self.customers < 1:
            raise ValueError("customers must be at least 1")
        if self.transactions < 0:
            raise ValueError("transactions cannot be negative")
        if self.merchants < 1:
            raise ValueError("merchants must be at least 1")
        if not 0 <= self.fraud_rate <= 1:
            raise ValueError("fraud_rate must be between 0 and 1")
        if self.as_of.tzinfo is None:
            raise ValueError("as_of must include a timezone")


def load_config(path: Path) -> GenerationConfig:
    """Load the human-readable V0 YAML into a typed configuration."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    values = raw["generation"]
    config = GenerationConfig(
        seed=int(values["seed"]),
        customers=int(values["customers"]),
        transactions=int(values["transactions"]),
        merchants=int(values["merchants"]),
        fraud_rate=float(values["fraud_rate"]),
        as_of=datetime.fromisoformat(values["as_of"]),
    )
    config.validate()
    return config

