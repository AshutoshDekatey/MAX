"""Command-line entry point for the V0 Dirty Bank."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from project_max.config import GenerationConfig
from project_max.generation.defects import inject_defects
from project_max.generation.orchestrator import generate_bank
from project_max.inspection.catalog import load_manifest
from project_max.persistence.postgres import bootstrap_database, load_generated_run


def _generation_config(args: argparse.Namespace) -> GenerationConfig:
    return GenerationConfig(
        seed=args.seed,
        customers=args.customers,
        transactions=args.transactions,
        merchants=args.merchants,
        fraud_rate=args.fraud_rate,
        as_of=datetime.fromisoformat(args.as_of),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="max-bank", description="Project MAX V0 source-system simulator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="generate one immutable Meridian Bank source run")
    generate.add_argument("--output", type=Path, default=None)
    generate.add_argument("--seed", type=int, default=20260820)
    generate.add_argument("--customers", type=int, default=100)
    generate.add_argument("--transactions", type=int, default=500)
    generate.add_argument("--merchants", type=int, default=50)
    generate.add_argument("--fraud-rate", type=float, default=0.06)
    generate.add_argument("--as-of", default="2026-08-20T12:00:00+00:00")
    generate.add_argument("--include-defects", action="store_true")
    generate.add_argument("--load-postgres", action="store_true")

    inject = subparsers.add_parser("inject-defects", help="add dirty extracts to an existing clean run")
    inject.add_argument("run_dir", type=Path)

    bootstrap = subparsers.add_parser("bootstrap-db", help="create the V0 PostgreSQL schemas")
    bootstrap.add_argument("--database-url", default=None)

    load = subparsers.add_parser("load-db", help="load an existing generated run into PostgreSQL")
    load.add_argument("run_dir", type=Path)
    load.add_argument("--database-url", default=None)

    inspect = subparsers.add_parser("inspect", help="print a generated run manifest")
    inspect.add_argument("run_dir", type=Path)
    return parser


def _database_url(explicit: str | None) -> str:
    value = explicit or os.getenv("MAX_DATABASE_URL")
    if not value:
        raise SystemExit("Set MAX_DATABASE_URL or pass --database-url. No credentials are created by Project MAX.")
    return value


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        output = args.output or Path(".local-data") / datetime.now(UTC).strftime("run_%Y%m%dT%H%M%SZ")
        database_url = _database_url(None) if args.load_postgres else None
        manifest = generate_bank(
            output,
            _generation_config(args),
            include_defects=args.include_defects,
            database_url=database_url,
        )
        print(json.dumps({"output": str(output), "counts": manifest["counts"]}, indent=2))
    elif args.command == "inject-defects":
        defects = inject_defects(args.run_dir)
        print(json.dumps({"run": str(args.run_dir), "defects": len(defects)}, indent=2))
    elif args.command == "bootstrap-db":
        bootstrap_database(_database_url(args.database_url))
        print("V0 PostgreSQL schemas created.")
    elif args.command == "load-db":
        load_generated_run(_database_url(args.database_url), args.run_dir)
        print(f"Loaded clean operational records from {args.run_dir}.")
    elif args.command == "inspect":
        print(json.dumps(load_manifest(args.run_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

