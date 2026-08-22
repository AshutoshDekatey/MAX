"""File catalog and safe previews for generated V0 source runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".txt", ".html", ".sql"}


def list_runs(base_dir: Path) -> list[Path]:
    if not base_dir.exists():
        return []
    direct_manifest = base_dir / "manifest.json"
    if direct_manifest.exists():
        return [base_dir]
    return sorted(
        [path.parent for path in base_dir.rglob("manifest.json")],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def list_source_files(run_dir: Path) -> list[Path]:
    return sorted(path for path in run_dir.rglob("*") if path.is_file())


def load_manifest(run_dir: Path) -> dict[str, Any]:
    return json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))


def preview_file(path: Path, limit: int = 25) -> tuple[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as stream:
            return "table", list(csv.DictReader(stream))[:limit]
    if suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()[:limit]]
        return "table", rows
    if suffix == ".json":
        return "json", json.loads(path.read_text(encoding="utf-8"))
    if suffix in TEXT_SUFFIXES:
        return "text", path.read_text(encoding="utf-8")[:12000]
    return "binary", {"name": path.name, "bytes": path.stat().st_size, "format": suffix.lstrip(".").upper()}

