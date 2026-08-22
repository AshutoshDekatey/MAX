"""Payment authorization event generator."""

from __future__ import annotations

import random
from datetime import timedelta

from project_max.config import GenerationConfig
from project_max.generation.common import iso


def generate_payments(
    config: GenerationConfig,
    cards: list[dict],
    devices: list[dict],
    merchants: list[dict],
    rng: random.Random,
) -> list[dict]:
    devices_by_customer: dict[str, list[dict]] = {}
    for device in devices:
        devices_by_customer.setdefault(device["customer_id"], []).append(device)

    rows = []
    for index in range(1, config.transactions + 1):
        card = rng.choice(cards)
        merchant = rng.choice(merchants)
        timestamp = config.as_of - timedelta(
            days=rng.randint(0, 30), seconds=rng.randint(0, 86399)
        )
        device = rng.choice(devices_by_customer[card["customer_id"]])
        amount = round(min(rng.lognormvariate(7.3, 1.05), 250000), 2)
        method = rng.choices(
            ["OTP", "BIOMETRIC", "3DS", "PASSWORD", "NONE"],
            [0.28, 0.18, 0.23, 0.06, 0.25],
        )[0]
        rows.append(
            {
                "event_id": f"PAYEVT{index:010d}",
                "schema_version": "1.0",
                "transaction_id": f"TXN{index:012d}",
                "card_token": card["card_token"],
                "customer_id": card["customer_id"],
                "merchant_id": merchant["merchant_id"],
                "amount": amount,
                "currency": "INR" if merchant["country_code"] == "IN" else rng.choice(["USD", "GBP", "SGD", "AED"]),
                "timestamp": iso(timestamp),
                "emitted_at": iso(timestamp + timedelta(milliseconds=rng.randint(20, 1200))),
                "country": merchant["country_code"],
                "channel": rng.choice(["ECOMMERCE", "POS", "CONTACTLESS", "ATM"]),
                "authentication_method": method,
                "device_id": device["device_id"],
                "authorization_result": rng.choices(["APPROVED", "DECLINED"], [0.94, 0.06])[0],
            }
        )
    rows.sort(key=lambda row: row["timestamp"])
    return rows

