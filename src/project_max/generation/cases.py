"""Fraud case records with structured fields and unstructured notes."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from project_max.generation.common import iso

NOTE_TEMPLATES = [
    "Customer denies making the transaction. Device history differs from normal mobile usage. Merchant outreach pending.",
    "Initial review found rapid spend after a password reset. Card blocked and replacement requested.",
    "Customer was travelling but could not identify this merchant. Authentication evidence has been requested.",
    "Merchant descriptor is ambiguous. Investigator compared prior activity and escalated for network evidence.",
]


def generate_fraud_cases(
    labels: list[dict], payments: list[dict], rng: random.Random
) -> list[dict]:
    payments_by_id = {row["transaction_id"]: row for row in payments}
    rows = []
    for index, label in enumerate(labels, start=1):
        payment = payments_by_id[label["transaction_id"]]
        opened_at = datetime.fromisoformat(label["reported_at"]) + timedelta(minutes=rng.randint(5, 240))
        rows.append(
            {
                "case_id": f"CASE{index:08d}",
                "transaction_id": label["transaction_id"],
                "customer_id": payment["customer_id"],
                "priority": rng.choices(["P2", "P3", "P4"], [0.2, 0.6, 0.2])[0],
                "status": rng.choice(["OPEN", "UNDER_REVIEW", "ESCALATED", "CLOSED"]),
                "queue": rng.choice(["CARD_FRAUD", "ACCOUNT_TAKEOVER", "MERCHANT_DISPUTES"]),
                "assigned_investigator": f"INV{rng.randint(1, 25):04d}",
                "opened_at": iso(opened_at),
                "closed_at": None,
                "investigator_notes": rng.choice(NOTE_TEMPLATES),
            }
        )
    return rows

