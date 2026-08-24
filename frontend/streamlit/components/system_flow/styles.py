"""Stable visual language for every Project MAX architecture definition."""

VIEWER_CSS = """
.max-flow-viewer {
  color-scheme: light;
  --surface: #ffffff;
  --panel: #f8fafc;
  --line: #64748b;
  --text: #0f172a;
  --muted: #64748b;
  --accent: #0f766e;
  box-sizing: border-box;
  padding: 18px 20px 16px;
  background: #ffffff;
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  min-height: 690px;
}
.max-flow-viewer * { box-sizing: border-box; }
.max-flow-viewer .eyebrow { color: var(--accent); font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
.max-flow-viewer h2 { margin: 5px 0 4px; font-size: 23px; letter-spacing: -.02em; color: var(--text); }
.max-flow-viewer .subtitle { color: var(--muted); font-size: 13px; margin-bottom: 12px; }
.max-flow-viewer .graph-shell { border: 1px solid #dbe3ec; border-radius: 14px; background: #ffffff; overflow: auto; }
.max-flow-viewer svg { width: 100%; min-width: 920px; height: auto; display: block; }
.max-flow-viewer .legend { display: flex; flex-wrap: wrap; gap: 10px 18px; padding: 12px 3px 5px; }
.max-flow-viewer .legend-item { display: inline-flex; gap: 7px; align-items: center; color: var(--muted); font-size: 11px; }
.max-flow-viewer .swatch { width: 10px; height: 10px; border-radius: 3px; }
.max-flow-viewer .new-summary { margin-top: 10px; border-left: 3px solid var(--accent); padding: 8px 11px; background: #f0fdfa; color: #134e4a; font-size: 12px; }
@keyframes reveal { to { stroke-dashoffset: 0; } }
@media (max-width: 720px) { .max-flow-viewer { padding: 12px; } .max-flow-viewer h2 { font-size: 19px; } }
"""

SVG_CSS = """
.edge { stroke: #64748b; stroke-width: 1.7; opacity: .82; marker-end: url(#arrow); }
.node { stroke-width: 1.6; rx: 10; filter: url(#shadow); }
.node-new { stroke-dasharray: 850; stroke-dashoffset: 0; }
.node-label { fill: #0f172a; font: 700 12px Inter, sans-serif; text-anchor: middle; }
.node-kind { fill: #475569; font: 9px Inter, sans-serif; text-anchor: middle; letter-spacing: .06em; }
.new-pill { fill: #ccfbf1; stroke: #0f766e; stroke-width: .8; }
.new-text { fill: #115e59; font: 800 8px Inter, sans-serif; text-anchor: middle; }
"""
