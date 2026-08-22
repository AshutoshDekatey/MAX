"""Device-intelligence source generator."""

from __future__ import annotations

import random
from datetime import timedelta

from faker import Faker

from project_max.config import GenerationConfig
from project_max.generation.common import iso


def generate_devices(
    config: GenerationConfig, customers: list[dict], rng: random.Random
) -> list[dict]:
    fake = Faker()
    fake.seed_instance(config.seed + 23)
    rows: list[dict] = []
    device_number = 1
    for customer in customers:
        for _ in range(rng.choices([1, 2], [0.8, 0.2])[0]):
            first_seen = config.as_of - timedelta(days=rng.randint(5, 900))
            last_seen = config.as_of - timedelta(minutes=rng.randint(0, 10080))
            rows.append(
                {
                    "device_id": f"DEV{device_number:08d}",
                    "customer_id": customer["customer_id"],
                    "ip": fake.ipv4_public(),
                    "browser": rng.choice(["Chrome", "Safari", "Edge", "Firefox", "BankApp"]),
                    "os": rng.choice(["Android", "iOS", "Windows", "macOS", "Linux"]),
                    "first_seen": iso(first_seen),
                    "last_seen": iso(max(first_seen, last_seen)),
                    "device_risk_signal": rng.choices(
                        ["TRUSTED", "NEW_DEVICE", "IP_REPUTATION", "EMULATOR_SUSPECTED"],
                        [0.78, 0.13, 0.06, 0.03],
                    )[0],
                }
            )
            device_number += 1
    return rows

