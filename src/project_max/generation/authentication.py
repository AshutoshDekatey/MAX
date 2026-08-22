"""Authentication-system event generator."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from project_max.generation.common import iso


def generate_authentication_events(payments: list[dict], rng: random.Random) -> list[dict]:
    rows: list[dict] = []
    for index, payment in enumerate(payments, start=1):
        method = payment["authentication_method"]
        if method == "OTP":
            event_type = rng.choices(["OTP_SUCCESS", "OTP_FAILED"], [0.9, 0.1])[0]
        elif method == "BIOMETRIC":
            event_type = "BIOMETRIC_SUCCESS"
        elif method == "3DS":
            event_type = "3DS_CHALLENGE"
        elif method == "PASSWORD":
            event_type = rng.choices(["PASSWORD_SUCCESS", "PASSWORD_FAILURE"], [0.86, 0.14])[0]
        else:
            event_type = rng.choices(["DEVICE_ENROLLED", "PASSIVE_AUTH"], [0.08, 0.92])[0]
        event_at = datetime.fromisoformat(payment["timestamp"]) - timedelta(seconds=rng.randint(1, 45))
        rows.append(
            {
                "auth_event_id": f"AUTHEVT{index:010d}",
                "transaction_id": payment["transaction_id"],
                "customer_id": payment["customer_id"],
                "device_id": payment["device_id"],
                "event_type": event_type,
                "event_timestamp": iso(event_at),
                "challenge_result": "FAILURE" if "FAILED" in event_type or "FAILURE" in event_type else "SUCCESS",
            }
        )
    return rows

