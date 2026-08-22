# ADR-0002: One config-driven System Flow Viewer

**Status:** Accepted from V0 onward

## Decision

Keep the Streamlit rendering component stable and define each cumulative architecture in a separate versioned graph file.

## Why

Thirteen independent diagrams would drift in visual language and become expensive to maintain. A validated graph contract supports nodes, edges, categories, descriptions, tooltips and current-version emphasis while keeping the user experience consistent.

## Consequence

Future versions extend architecture definitions and may improve the renderer compatibly, but must not redesign the viewer per version.

