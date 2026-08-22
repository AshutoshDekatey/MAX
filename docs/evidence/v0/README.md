# V0 evidence

This directory preserves reproducible evidence for the V0 historical snapshot.

- `system-flow-viewer.png`: required screenshot of the standing architecture viewer
- `system-flow-viewer.svg`: deterministic evidence render generated from the same graph definition and SVG renderer used by Streamlit
- `verification.txt`: test, lint and sample-generation evidence captured at completion

Measured outputs are recorded only after commands execute. No performance or scale benchmark is claimed in V0.

The live Streamlit application and dialog are exercised with Streamlit's application test framework. The PNG is rasterized from the shared viewer renderer because the isolated cloud browser cannot address the local application container directly.
