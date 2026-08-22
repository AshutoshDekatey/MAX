"""Stable visual language for every Project MAX architecture definition."""

VIEWER_CSS = """
.max-flow-viewer {
  color-scheme: dark;
  --surface: #0b1220;
  --panel: #111b2e;
  --line: #6f819d;
  --text: #edf3fb;
  --muted: #a7b4c7;
  --accent: #41d3bd;
  box-sizing: border-box;
  padding: 18px 20px 16px;
  background: linear-gradient(145deg, #0b1220, #0d1728);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  min-height: 690px;
}
.max-flow-viewer * { box-sizing: border-box; }
.max-flow-viewer .eyebrow { color: var(--accent); font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
.max-flow-viewer h2 { margin: 5px 0 4px; font-size: 23px; letter-spacing: -.02em; }
.max-flow-viewer .subtitle { color: var(--muted); font-size: 13px; margin-bottom: 12px; }
.max-flow-viewer .graph-shell { border: 1px solid #25344d; border-radius: 14px; background: rgba(8, 15, 27, .8); overflow: auto; }
.max-flow-viewer svg { width: 100%; min-width: 920px; height: auto; display: block; }
.max-flow-viewer .legend { display: flex; flex-wrap: wrap; gap: 10px 18px; padding: 12px 3px 5px; }
.max-flow-viewer .legend-item { display: inline-flex; gap: 7px; align-items: center; color: var(--muted); font-size: 11px; }
.max-flow-viewer .swatch { width: 10px; height: 10px; border-radius: 3px; }
.max-flow-viewer .new-summary { margin-top: 10px; border-left: 3px solid var(--accent); padding: 8px 11px; background: #101c2f; color: #d7e2ef; font-size: 12px; }
@keyframes reveal { to { stroke-dashoffset: 0; } }
@media (max-width: 720px) { .max-flow-viewer { padding: 12px; } .max-flow-viewer h2 { font-size: 19px; } }
"""

SVG_CSS = """
.edge { stroke: #6f819d; stroke-width: 1.6; opacity: .7; marker-end: url(#arrow); }
.node { stroke-width: 1.6; rx: 10; filter: url(#shadow); }
.node-new { stroke-dasharray: 850; stroke-dashoffset: 0; }
.node-label { fill: #edf3fb; font: 700 12px Inter, sans-serif; text-anchor: middle; }
.node-kind { fill: #c6d1df; font: 9px Inter, sans-serif; text-anchor: middle; letter-spacing: .06em; }
.new-pill { fill: #41d3bd; }
.new-text { fill: #051311; font: 800 8px Inter, sans-serif; text-anchor: middle; }
"""
