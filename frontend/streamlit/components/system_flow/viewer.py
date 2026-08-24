"""Render any cumulative Project MAX graph using the standing visual grammar."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st

from .styles import SVG_CSS, VIEWER_CSS


def load_architecture(path: Path) -> dict[str, Any]:
    graph = json.loads(path.read_text(encoding="utf-8"))
    validate_architecture(graph)
    return graph


def validate_architecture(graph: dict[str, Any]) -> None:
    required = {"version", "title", "new_in_version", "categories", "nodes", "edges"}
    missing = required - graph.keys()
    if missing:
        raise ValueError(f"Architecture definition missing: {sorted(missing)}")
    node_ids = [node["id"] for node in graph["nodes"]]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Architecture node IDs must be unique")
    category_ids = {category["id"] for category in graph["categories"]}
    unknown_categories = {node["category"] for node in graph["nodes"]} - category_ids
    if unknown_categories:
        raise ValueError(f"Unknown node categories: {sorted(unknown_categories)}")
    for edge in graph["edges"]:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError(f"Edge references an unknown node: {edge}")


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def build_viewer_svg(graph: dict[str, Any]) -> str:
    validate_architecture(graph)
    categories = {item["id"]: item for item in graph["categories"]}
    nodes = {item["id"]: item for item in graph["nodes"]}
    width, height = graph.get("canvas", {}).get("width", 1040), graph.get("canvas", {}).get("height", 650)
    node_width, node_height = 220, 82

    edge_svg = []
    for edge in graph["edges"]:
        source, target = nodes[edge["from"]], nodes[edge["to"]]
        source_x = source["x"] + node_width / 2
        source_y = source["y"] + node_height / 2
        target_x = target["x"] + node_width / 2
        target_y = target["y"] + node_height / 2
        delta_x, delta_y = target_x - source_x, target_y - source_y
        boundary_scale = 1 / max(
            abs(delta_x) / (node_width / 2),
            abs(delta_y) / (node_height / 2),
        )
        x1 = source_x + delta_x * boundary_scale
        y1 = source_y + delta_y * boundary_scale
        arrow_gap = boundary_scale + 0.018
        x2 = target_x - delta_x * arrow_gap
        y2 = target_y - delta_y * arrow_gap
        edge_svg.append(
            f'<line class="edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><title>{_escape(edge.get("description", "Data flow"))}</title></line>'
        )

    node_svg = []
    for node in graph["nodes"]:
        category = categories[node["category"]]
        introduced = node.get("introduced_in") == graph["version"]
        css_class = "node node-new" if introduced else "node"
        x, y = node["x"], node["y"]
        label = _escape(node["label"])
        node_svg.append(
            f'<g><rect class="{css_class}" x="{x}" y="{y}" width="{node_width}" height="{node_height}" fill="{_escape(category["color"])}" stroke="{_escape(category["stroke"])}"><title>{_escape(node.get("tooltip", node.get("description", "")))}</title></rect>'
            f'<text class="node-label" x="{x + node_width / 2}" y="{y + 37}">{label}</text>'
            f'<text class="node-kind" x="{x + node_width / 2}" y="{y + 59}">{_escape(category["label"])}</text>'
            + (
                f'<rect class="new-pill" x="{x + 121}" y="{y + 7}" width="60" height="16" rx="8"/><text class="new-text" x="{x + 151}" y="{y + 18}">NEW IN {graph["version"]}</text>'
                if introduced
                else ""
            )
            + "</g>"
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{_escape(graph['title'])}">
<style>{SVG_CSS}</style>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker><filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity=".14"/></filter></defs>
<rect width="100%" height="100%" fill="#ffffff"/>
{''.join(edge_svg)}{''.join(node_svg)}</svg>"""


def build_viewer_html(graph: dict[str, Any]) -> str:
    validate_architecture(graph)
    legend = "".join(
        f'<span class="legend-item"><span class="swatch" style="background:{_escape(item["color"])};border:1px solid {_escape(item["stroke"])}"></span>{_escape(item["label"])}</span>'
        for item in graph["categories"]
    )
    return f"""<style>{VIEWER_CSS}</style><section class="max-flow-viewer">
<div class="eyebrow">Project MAX — {graph['version']}</div><h2>{_escape(graph['title'])}</h2>
<div class="subtitle">{_escape(graph.get('subtitle', 'Cumulative architecture'))}</div>
<div class="legend">{legend}</div>
<div class="new-summary"><strong>New in this version:</strong> {_escape(graph['new_in_version'])}</div></section>"""


def render_system_flow(path: Path) -> None:
    graph = load_architecture(path)
    # st.image renders SVG directly and avoids HTML sanitization removing parts of
    # the diagram. Header/legend remain regular sanitized Streamlit HTML.
    st.html(build_viewer_html(graph), width="stretch")
    st.image(build_viewer_svg(graph), width="stretch")
