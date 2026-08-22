"""Coordinate independent V0 source systems without unifying their raw formats."""

from __future__ import annotations

import hashlib
import os
import random
from pathlib import Path

from project_max.config import GenerationConfig
from project_max.generation.authentication import generate_authentication_events
from project_max.generation.cases import generate_fraud_cases
from project_max.generation.common import write_csv, write_json, write_jsonl
from project_max.generation.core_banking import generate_core_banking
from project_max.generation.defects import inject_defects
from project_max.generation.devices import generate_devices
from project_max.generation.documents import generate_documents
from project_max.generation.fraud import generate_fraud_labels
from project_max.generation.merchants import generate_merchants
from project_max.generation.payments import generate_payments


def _file_inventory(root: Path) -> list[dict]:
    inventory = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item.name != "manifest.json"):
        data = path.read_bytes()
        inventory.append(
            {
                "path": str(path.relative_to(root)),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return inventory


def generate_bank(
    output_dir: Path,
    config: GenerationConfig,
    *,
    include_defects: bool = False,
    database_url: str | None = None,
) -> dict:
    """Generate one immutable, reproducible snapshot of the V0 bank."""
    config.validate()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty run directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(config.seed)

    core = generate_core_banking(config, rng)
    for table_name, rows in core.items():
        write_csv(output_dir / "core_banking" / f"{table_name}.csv", rows)

    merchants = generate_merchants(config, rng)
    merchant_filename = f"merchant_reference_{config.as_of:%Y_%m_%d}.csv"
    write_csv(output_dir / "merchant_reference" / merchant_filename, merchants)

    devices = generate_devices(config, core["customers"], rng)
    write_jsonl(output_dir / "device_intelligence" / "devices.jsonl", devices)

    payments = generate_payments(config, core["cards"], devices, merchants, rng)
    write_jsonl(output_dir / "payments" / "payment_authorizations.jsonl", payments)

    auth_events = generate_authentication_events(payments, rng)
    write_jsonl(output_dir / "authentication" / "authentication_events.jsonl", auth_events)

    fraud_labels = generate_fraud_labels(config, payments, rng)
    write_csv(output_dir / "fraud_labels" / "fraud_chargebacks.csv", fraud_labels)

    fraud_cases = generate_fraud_cases(fraud_labels, payments, rng)
    write_jsonl(output_dir / "fraud_cases" / "fraud_cases.jsonl", fraud_cases)

    document_metadata = generate_documents(output_dir / "banking_documents")
    defect_ledger = inject_defects(output_dir) if include_defects else []

    database_loaded = False
    if database_url:
        from project_max.persistence.postgres import load_generated_run

        load_generated_run(database_url, output_dir)
        database_loaded = True

    counts = {
        **{name: len(rows) for name, rows in core.items()},
        "merchants": len(merchants),
        "devices": len(devices),
        "payments": len(payments),
        "authentication_events": len(auth_events),
        "fraud_labels": len(fraud_labels),
        "fraud_cases": len(fraud_cases),
        "documents": len(document_metadata),
        "defects": len(defect_ledger),
    }
    manifest = {
        "project": "Project MAX",
        "version": "V0",
        "bank": "Meridian Bank",
        "purpose": "synthetic operational source-system simulation",
        "seed": config.seed,
        "as_of": config.as_of.isoformat(timespec="seconds"),
        "base_currency": "INR",
        "counts": counts,
        "document_catalog": document_metadata,
        "database_loaded": database_loaded,
        "database_url_present": bool(database_url or os.getenv("MAX_DATABASE_URL")),
        "files": _file_inventory(output_dir),
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest

