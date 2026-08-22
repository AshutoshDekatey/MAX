"""Daily merchant reference feed generator."""

from __future__ import annotations

import random
from datetime import timedelta

from faker import Faker

from project_max.config import GenerationConfig

MCCS = [
    ("5411", "GROCERY"),
    ("5812", "RESTAURANT"),
    ("5732", "ELECTRONICS"),
    ("4511", "AIRLINE"),
    ("7011", "HOTEL"),
    ("5999", "RETAIL"),
    ("4829", "MONEY_TRANSFER"),
    ("5967", "ONLINE_MARKETPLACE"),
]


def generate_merchants(config: GenerationConfig, rng: random.Random) -> list[dict]:
    fake = Faker("en_IN")
    fake.seed_instance(config.seed + 11)
    countries = ["IN", "IN", "IN", "SG", "AE", "GB", "US"]
    rows = []
    for index in range(1, config.merchants + 1):
        mcc, category = rng.choice(MCCS)
        updated = config.as_of - timedelta(days=rng.randint(0, 5))
        rows.append(
            {
                "merchant_id": f"MER{index:06d}",
                "merchant_name": fake.company(),
                "merchant_category_code": mcc,
                "merchant_category": category,
                "country_code": rng.choice(countries),
                "risk_tier": rng.choices(["LOW", "MEDIUM", "HIGH"], [0.72, 0.23, 0.05])[0],
                "status": "ACTIVE",
                "reference_updated_at": updated.isoformat(timespec="seconds"),
            }
        )
    return rows

