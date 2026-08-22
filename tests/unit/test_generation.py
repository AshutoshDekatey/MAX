from __future__ import annotations

import csv
import json
from datetime import datetime

import pytest

from project_max.config import GenerationConfig
from project_max.generation.common import read_jsonl
from project_max.generation.defects import DEFECT_TYPES
from project_max.generation.orchestrator import generate_bank


@pytest.fixture
def config() -> GenerationConfig:
    return GenerationConfig(
        seed=42,
        customers=12,
        transactions=80,
        merchants=9,
        fraud_rate=0.12,
        as_of=datetime.fromisoformat("2026-08-20T12:00:00+00:00"),
    )


def _csv_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_full_generation_has_cross_system_integrity(tmp_path, config):
    run = tmp_path / "run"
    manifest = generate_bank(run, config, include_defects=True)

    customers = _csv_rows(run / "core_banking" / "customers.csv")
    cards = _csv_rows(run / "core_banking" / "cards.csv")
    merchants = _csv_rows(next((run / "merchant_reference").glob("*.csv")))
    devices = read_jsonl(run / "device_intelligence" / "devices.jsonl")
    payments = read_jsonl(run / "payments" / "payment_authorizations.jsonl")
    auth = read_jsonl(run / "authentication" / "authentication_events.jsonl")

    assert manifest["version"] == "V0"
    assert manifest["counts"]["customers"] == 12
    assert manifest["counts"]["payments"] == 80
    assert {row["customer_id"] for row in payments} <= {row["customer_id"] for row in customers}
    assert {row["card_token"] for row in payments} <= {row["card_token"] for row in cards}
    assert {row["merchant_id"] for row in payments} <= {row["merchant_id"] for row in merchants}
    assert {row["device_id"] for row in payments} <= {row["device_id"] for row in devices}
    assert {row["transaction_id"] for row in auth} == {row["transaction_id"] for row in payments}


def test_fraud_labels_are_delayed(tmp_path, config):
    run = tmp_path / "run"
    generate_bank(run, config)
    payments = {
        row["transaction_id"]: row
        for row in read_jsonl(run / "payments" / "payment_authorizations.jsonl")
    }
    labels = _csv_rows(run / "fraud_labels" / "fraud_chargebacks.csv")

    assert labels
    for label in labels:
        payment_at = datetime.fromisoformat(payments[label["transaction_id"]]["timestamp"])
        reported_at = datetime.fromisoformat(label["reported_at"])
        assert reported_at > payment_at
        assert int(label["label_delay_days"]) >= 2


def test_every_required_defect_is_ledgered(tmp_path, config):
    run = tmp_path / "run"
    generate_bank(run, config, include_defects=True)
    ledger = json.loads((run / "dirty" / "defect_ledger.json").read_text(encoding="utf-8"))

    assert {item["defect_type"] for item in ledger["defects"]} == DEFECT_TYPES
    original = run / "dirty" / "merchant_reference" / "merchant_reference_dirty.csv"
    duplicate = run / "dirty" / "merchant_reference" / "merchant_reference_dirty_COPY.csv"
    assert original.read_bytes() == duplicate.read_bytes()


def test_document_repository_includes_ocr_candidate(tmp_path, config):
    run = tmp_path / "run"
    manifest = generate_bank(run, config)
    catalog = manifest["document_catalog"]
    formats = {item["format"] for item in catalog}

    assert {"PDF", "DOCX", "TXT", "HTML", "PDF_IMAGE_ONLY"} <= formats
    ocr_item = next(item for item in catalog if item["ocr_candidate"])
    assert (run / "banking_documents" / ocr_item["file"]).exists()


def test_same_seed_repeats_structured_records(tmp_path, config):
    first, second = tmp_path / "first", tmp_path / "second"
    generate_bank(first, config)
    generate_bank(second, config)

    relative_paths = [
        "core_banking/customers.csv",
        "payments/payment_authorizations.jsonl",
        "authentication/authentication_events.jsonl",
        "device_intelligence/devices.jsonl",
        "fraud_labels/fraud_chargebacks.csv",
    ]
    for relative in relative_paths:
        assert first.joinpath(relative).read_bytes() == second.joinpath(relative).read_bytes()


def test_generator_refuses_to_overwrite(tmp_path, config):
    run = tmp_path / "run"
    generate_bank(run, config)
    with pytest.raises(FileExistsError):
        generate_bank(run, config)


def test_config_rejects_impossible_counts():
    with pytest.raises(ValueError, match="customers"):
        GenerationConfig(customers=0).validate()

