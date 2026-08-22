"""Delayed fraud and chargeback label generator."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from project_max.config import GenerationConfig
from project_max.generation.common import iso

FRAUD_REASONS = [
    "CARD_NOT_PRESENT_FRAUD",
    "ACCOUNT_TAKEOVER",
    "LOST_OR_STOLEN_CARD",
    "MERCHANT_DISPUTE",
    "SOCIAL_ENGINEERING",
]


def generate_fraud_labels(
    config: GenerationConfig, payments: list[dict], rng: random.Random
) -> list[dict]:
    candidates = [row for row in payments if row["authorization_result"] == "APPROVED"]
    selected = [row for row in candidates if rng.random() < config.fraud_rate]
    if candidates and config.fraud_rate > 0 and not selected:
        selected = [rng.choice(candidates)]

    labels = []
    for index, payment in enumerate(selected, start=1):
        transaction_at = datetime.fromisoformat(payment["timestamp"])
        reported_at = transaction_at + timedelta(days=rng.randint(2, 21), hours=rng.randint(0, 23))
        labels.append(
            {
                "fraud_label_id": f"FRD{index:08d}",
                "transaction_id": payment["transaction_id"],
                "label": "CONFIRMED_FRAUD",
                "fraud_reason": rng.choice(FRAUD_REASONS),
                "reported_at": iso(reported_at),
                "label_delay_days": (reported_at.date() - transaction_at.date()).days,
                "chargeback_amount": payment["amount"],
                "chargeback_currency": payment["currency"],
                "source": rng.choice(["CUSTOMER_REPORT", "BANK_REVIEW", "NETWORK_ALERT"]),
            }
        )
    return labels

