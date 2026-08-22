"""Controlled bad-data injection for the dirty-bank prototype."""

from __future__ import annotations

import csv
import shutil
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

from project_max.generation.common import read_jsonl, write_csv, write_json, write_jsonl

DEFECT_TYPES = {
    "null_values",
    "duplicate_records",
    "duplicate_transaction_events",
    "inconsistent_country_codes",
    "inconsistent_currencies",
    "malformed_timestamps",
    "wrong_data_types",
    "late_records",
    "delayed_fraud_labels",
    "stale_reference_data",
    "unexpected_categories",
    "merchant_name_variations",
    "schema_changes",
    "invalid_foreign_keys",
    "duplicated_files",
}


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def inject_defects(run_dir: Path) -> list[dict]:
    """Create dirty copies and return a complete ledger of intentional defects."""
    dirty = run_dir / "dirty"
    dirty.mkdir(parents=True, exist_ok=False)
    ledger: list[dict] = []

    def record(defect_type: str, target: str, record_id: str, detail: str) -> None:
        ledger.append(
            {
                "defect_id": f"DEF{len(ledger) + 1:04d}",
                "defect_type": defect_type,
                "target": target,
                "record_id": record_id,
                "description": detail,
            }
        )

    customers = _read_csv(run_dir / "core_banking" / "customers.csv")
    if customers:
        customers[0]["email"] = ""
        record("null_values", "dirty/core_banking/customers_dirty.csv", customers[0]["customer_id"], "email is null")
        customers.append(deepcopy(customers[0]))
        record("duplicate_records", "dirty/core_banking/customers_dirty.csv", customers[-1]["customer_id"], "exact customer row repeated")
    write_csv(dirty / "core_banking" / "customers_dirty.csv", customers)

    payments = read_jsonl(run_dir / "payments" / "payment_authorizations.jsonl")
    dirty_payments = deepcopy(payments)
    if dirty_payments:
        dirty_payments.append(deepcopy(dirty_payments[0]))
        record("duplicate_transaction_events", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[0]["event_id"], "same payment event emitted twice")
    if len(dirty_payments) > 1:
        dirty_payments[1]["country"] = "IND"
        record("inconsistent_country_codes", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[1]["event_id"], "ISO-2 country changed to IND")
    if len(dirty_payments) > 2:
        dirty_payments[2]["currency"] = "Rs"
        record("inconsistent_currencies", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[2]["event_id"], "non-ISO currency Rs")
    if len(dirty_payments) > 3:
        dirty_payments[3]["timestamp"] = "20-08-2026 25:61:00"
        record("malformed_timestamps", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[3]["event_id"], "unparseable timestamp")
    if len(dirty_payments) > 4:
        dirty_payments[4]["amount"] = "one thousand rupees"
        record("wrong_data_types", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[4]["event_id"], "amount changed from number to text")
    if len(dirty_payments) > 5:
        original = datetime.fromisoformat(dirty_payments[5]["timestamp"])
        dirty_payments[5]["emitted_at"] = (original + timedelta(days=4)).isoformat(timespec="seconds")
        record("late_records", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[5]["event_id"], "emitted four days after event time")
    if len(dirty_payments) > 6:
        dirty_payments[6]["channel"] = "SMART_RING"
        record("unexpected_categories", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[6]["event_id"], "new undocumented channel")
    if len(dirty_payments) > 7:
        dirty_payments[7]["schema_version"] = "2.0"
        dirty_payments[7]["merchant_region"] = "APAC"
        record("schema_changes", "dirty/payments/payment_authorizations_dirty.jsonl", dirty_payments[7]["event_id"], "v2 field appears in a v1 stream")
    write_jsonl(dirty / "payments" / "payment_authorizations_dirty.jsonl", dirty_payments)

    devices = read_jsonl(run_dir / "device_intelligence" / "devices.jsonl")
    if devices:
        devices[0]["customer_id"] = "CUS_DOES_NOT_EXIST"
        record("invalid_foreign_keys", "dirty/device_intelligence/devices_dirty.jsonl", devices[0]["device_id"], "device references an unknown customer")
    write_jsonl(dirty / "device_intelligence" / "devices_dirty.jsonl", devices)

    merchant_files = list((run_dir / "merchant_reference").glob("merchant_reference_*.csv"))
    if merchant_files:
        merchants = _read_csv(merchant_files[0])
        if merchants:
            merchants[0]["reference_updated_at"] = "2025-01-01T00:00:00+00:00"
            record("stale_reference_data", "dirty/merchant_reference/merchant_reference_dirty.csv", merchants[0]["merchant_id"], "reference date is intentionally stale")
        if len(merchants) > 1:
            merchants[1]["merchant_name"] = "  " + merchants[1]["merchant_name"].upper().replace("LIMITED", "LTD") + "  "
            record("merchant_name_variations", "dirty/merchant_reference/merchant_reference_dirty.csv", merchants[1]["merchant_id"], "case, spacing and suffix variation")
        target = dirty / "merchant_reference" / "merchant_reference_dirty.csv"
        write_csv(target, merchants)
        duplicate = target.with_name("merchant_reference_dirty_COPY.csv")
        shutil.copyfile(target, duplicate)
        record("duplicated_files", str(duplicate.relative_to(run_dir)), "FILE", "byte-identical merchant feed copy")

    fraud_file = run_dir / "fraud_labels" / "fraud_chargebacks.csv"
    fraud_rows = _read_csv(fraud_file)
    write_csv(dirty / "fraud_labels" / "fraud_chargebacks_dirty.csv", fraud_rows)
    label_id = fraud_rows[0]["fraud_label_id"] if fraud_rows else "NO_LABEL_GENERATED"
    record("delayed_fraud_labels", "fraud_labels/fraud_chargebacks.csv", label_id, "labels arrive 2-21 days after transaction time by design")

    missing = DEFECT_TYPES - {item["defect_type"] for item in ledger}
    if missing:
        raise RuntimeError(f"Defect injector failed to create: {sorted(missing)}")
    write_json(dirty / "defect_ledger.json", {"version": "V0", "defects": ledger})
    return ledger

