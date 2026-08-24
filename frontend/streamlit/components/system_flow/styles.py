"""Stable visual language for every Project MAX architecture definition."""

VIEWER_CSS = """
.max-flow-viewer {
  color-scheme: light;
  --text: #0f172a;
  --muted: #64748b;
  --accent: #0f766e;
  box-sizing: border-box;
  padding: 4px 8px 10px;
  background: #ffffff;
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

.max-flow-viewer * { box-sizing: border-box; }

.max-flow-viewer .eyebrow {
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.max-flow-viewer h2 {
  margin: 4px 0;
  font-size: 24px;
  color: var(--text);
}

.max-flow-viewer .subtitle {
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 8px;
}

.max-flow-viewer .legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding: 6px 0;
}

.max-flow-viewer .legend-item {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  color: var(--muted);
  font-size: 12px;
}

.max-flow-viewer .swatch {
  width: 11px;
  height: 11px;
  border-radius: 3px;
}

.max-flow-viewer .new-summary {
  margin-top: 6px;
  border-left: 3px solid var(--accent);
  padding: 7px 10px;
  background: #f0fdfa;
  color: #134e4a;
  font-size: 12px;
}

@media (max-width: 720px) {
  .max-flow-viewer h2 { font-size: 20px; }
}
"""

SVG_CSS = """
.edge {
  stroke: #64748b;
  stroke-width: 2;
  opacity: .85;
  marker-end: url(#arrow);
}

.node {
  stroke-width: 1.8;
  rx: 11;
  filter: url(#shadow);
}

.node-new {
  stroke-dasharray: 850;
  stroke-dashoffset: 0;
}

.node-label {
  fill: #0f172a;
  font: 700 15px Inter, sans-serif;
  text-anchor: middle;
}

.node-kind {
  fill: #475569;
  font: 11px Inter, sans-serif;
  text-anchor: middle;
  letter-spacing: .04em;
}

.new-pill {
  fill: #ccfbf1;
  stroke: #0f766e;
  stroke-width: .8;
}

.new-text {
  fill: #115e59;
  font: 800 8px Inter, sans-serif;
  text-anchor: middle;
}
"""
