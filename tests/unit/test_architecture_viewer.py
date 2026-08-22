from __future__ import annotations

import json
from pathlib import Path

import pytest

from frontend.streamlit.components.system_flow.viewer import (
    build_viewer_html,
    load_architecture,
    validate_architecture,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
V0_GRAPH = REPO_ROOT / "frontend" / "streamlit" / "architecture" / "v0.json"


def test_v0_architecture_is_complete_and_renderable():
    graph = load_architecture(V0_GRAPH)
    html = build_viewer_html(graph)

    assert graph["version"] == "V0"
    assert len(graph["nodes"]) >= 12
    assert "Source Systems Simulator" in html
    assert "NEW IN V0" in html
    assert "New in this version" in html
    assert "marker-end" in html


def test_viewer_rejects_unknown_edge_target():
    graph = json.loads(V0_GRAPH.read_text(encoding="utf-8"))
    graph["edges"].append({"from": "simulator", "to": "not-real"})
    with pytest.raises(ValueError, match="unknown node"):
        validate_architecture(graph)

