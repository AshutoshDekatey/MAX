"""Synthetic records for Meridian's PostgreSQL core customer system."""

from __future__ import annotations

import random
from datetime import timedelta

from faker import Faker

from project_max.config import GenerationConfig
from project_max.generation.common import iso


def generate_core_banking(config: GenerationConfig, rng: random.Random) -> dict[str, list[dict]]:
    fake = Faker("en_IN")
    fake.seed_instance(config.seed)
    customers: list[dict] = []
    accounts: list[dict] = []
    cards: list[dict] = []
    addresses: list[dict] = []
    history: list[dict] = []
    card_number = 1
    account_number = 1

    for index in range(1, config.customers + 1):
        customer_id = f"CUS{index:07d}"
        created_at = config.as_of - timedelta(days=rng.randint(60, 3650))
        status = rng.choices(["ACTIVE", "DORMANT", "REVIEW"], [0.91, 0.06, 0.03])[0]
        customers.append(
            {
                "customer_id": customer_id,
                "full_name": fake.name(),
                "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=85).isoformat(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "kyc_status": rng.choices(["VERIFIED", "PENDING", "EXPIRED"], [0.9, 0.07, 0.03])[0],
                "customer_status": status,
                "created_at": iso(created_at),
                "updated_at": iso(config.as_of - timedelta(days=rng.randint(0, 30))),
            }
        )
        addresses.append(
            {
                "address_id": f"ADR{index:07d}",
                "customer_id": customer_id,
                "address_type": "PRIMARY",
                "line_1": fake.street_address(),
                "city": fake.city(),
                "state": fake.state(),
                "postal_code": fake.postcode(),
                "country_code": "IN",
                "valid_from": created_at.date().isoformat(),
                "valid_to": None,
            }
        )
        history.append(
            {
                "history_id": f"CSH{index:07d}",
                "customer_id": customer_id,
                "status": status,
                "effective_from": iso(created_at),
                "effective_to": None,
                "reason": "ACCOUNT_OPENING" if status == "ACTIVE" else "PERIODIC_REVIEW",
            }
        )

        for _ in range(rng.choices([1, 2], [0.84, 0.16])[0]):
            account_id = f"ACC{account_number:08d}"
            account_number += 1
            account_type = rng.choices(["SAVINGS", "CURRENT", "CREDIT"], [0.67, 0.18, 0.15])[0]
            accounts.append(
                {
                    "account_id": account_id,
                    "customer_id": customer_id,
                    "account_type": account_type,
                    "currency": "INR",
                    "status": "OPEN" if status == "ACTIVE" else "RESTRICTED",
                    "opened_at": iso(created_at + timedelta(days=rng.randint(0, 7))),
                    "closed_at": None,
                }
            )
            card_id = f"CRD{card_number:08d}"
            cards.append(
                {
                    "card_id": card_id,
                    "account_id": account_id,
                    "customer_id": customer_id,
                    "card_token": f"tok_meridian_{card_number:012d}",
                    "card_network": rng.choice(["VISA", "MASTERCARD", "RUPAY"]),
                    "card_type": "CREDIT" if account_type == "CREDIT" else "DEBIT",
                    "status": "ACTIVE" if status == "ACTIVE" else "BLOCKED",
                    "issued_at": iso(created_at + timedelta(days=rng.randint(1, 14))),
                    "expires_on": (config.as_of + timedelta(days=rng.randint(365, 1460))).date().isoformat(),
                }
            )
            card_number += 1

    return {
        "customers": customers,
        "accounts": accounts,
        "cards": cards,
        "addresses": addresses,
        "customer_status_history": history,
    }

