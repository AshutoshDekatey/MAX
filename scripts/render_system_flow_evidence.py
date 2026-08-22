"""Write a standalone SVG evidence render from the live viewer definition."""

import sys
from html import escape
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from frontend.streamlit.components.system_flow.viewer import (  # noqa: E402
    build_viewer_svg,
    load_architecture,
)

ARCHITECTURE = REPOSITORY_ROOT / "frontend" / "streamlit" / "architecture" / "v0.json"
OUTPUT = REPOSITORY_ROOT / "docs" / "evidence" / "v0" / "system-flow-viewer.svg"
PNG_OUTPUT = REPOSITORY_ROOT / "docs" / "evidence" / "v0" / "system-flow-viewer.png"


def build_evidence_svg() -> str:
    graph = load_architecture(ARCHITECTURE)
    graph_svg = build_viewer_svg(graph)
    legend = []
    for index, category in enumerate(graph["categories"]):
        x = 50 + index * 255
        legend.append(
            f'<rect x="{x}" y="795" width="14" height="14" rx="3" fill="{category["color"]}" stroke="{category["stroke"]}"/>'
            f'<text x="{x + 22}" y="807" class="legend">{escape(category["label"])}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="900" viewBox="0 0 1120 900">
<style>
.heading {{ fill:#edf3fb; font:700 26px Inter,sans-serif; }}
.eyebrow {{ fill:#41d3bd; font:700 12px Inter,sans-serif; letter-spacing:.12em; }}
.subtitle {{ fill:#a7b4c7; font:13px Inter,sans-serif; }}
.legend {{ fill:#c6d1df; font:12px Inter,sans-serif; }}
.summary {{ fill:#d7e2ef; font:13px Inter,sans-serif; }}
</style>
<rect width="1120" height="900" fill="#0b1220"/>
<text x="40" y="30" class="eyebrow">PROJECT MAX — {escape(graph['version'])}</text>
<text x="40" y="62" class="heading">{escape(graph['title'])}</text>
<text x="40" y="86" class="subtitle">{escape(graph['subtitle'])}</text>
<svg x="40" y="110" width="1040" height="650">{graph_svg}</svg>
{''.join(legend)}
<rect x="40" y="830" width="1040" height="48" rx="5" fill="#101c2f"/>
<rect x="40" y="830" width="4" height="48" fill="#41d3bd"/>
<text x="58" y="850" class="summary" font-weight="700">New in this version:</text>
<text x="58" y="869" class="summary">{escape(graph['new_in_version'])}</text>
</svg>"""


if __name__ == "__main__":
    import cairosvg

    svg = build_evidence_svg()
    OUTPUT.write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(PNG_OUTPUT), output_width=1680)
    print(OUTPUT)
    print(PNG_OUTPUT)
