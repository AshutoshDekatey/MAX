"""Project MAX V0 - Source Systems Simulator."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from frontend.streamlit.components.system_flow import render_system_flow
from project_max.config import GenerationConfig
from project_max.generation import generate_bank
from project_max.inspection.catalog import list_runs, list_source_files, load_manifest, preview_file

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = Path(__file__).parent / "architecture" / "v0.json"
RUNS_ROOT = REPOSITORY_ROOT / ".local-data"

st.set_page_config(page_title="Project MAX — V0", page_icon="🏦", layout="wide")
st.markdown(
    """<style>
    .block-container {padding-top: 1.4rem; max-width: 1500px;}
    [data-testid="stMetric"] {border: 1px solid #dfe6ee; padding: .7rem 1rem; border-radius: .65rem;}
    .max-note {padding: .8rem 1rem; border-left: 4px solid #137c8b; background: #f2f7f8; border-radius: .25rem;}
    </style>""",
    unsafe_allow_html=True,
)


@st.dialog("Project MAX — System Flow", width="large")
def system_flow_dialog() -> None:
    st.caption("V0 cumulative architecture. Use the × control above to close.")
    render_system_flow(ARCHITECTURE)


def make_config(*, fraud_only: bool = False) -> GenerationConfig:
    return GenerationConfig(
        seed=int(st.session_state.seed),
        customers=int(st.session_state.customers),
        transactions=int(st.session_state.transactions),
        merchants=int(st.session_state.merchants),
        fraud_rate=0.18 if fraud_only else float(st.session_state.fraud_rate),
        as_of=datetime.fromisoformat(st.session_state.as_of),
    )


def create_run(action: str, *, include_defects: bool = False, fraud_only: bool = False) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = RUNS_ROOT / f"{action}_{stamp}_{uuid4().hex[:6]}"
    config = make_config(fraud_only=fraud_only)
    if action == "customers":
        config = GenerationConfig(
            seed=config.seed,
            customers=config.customers,
            transactions=0,
            merchants=config.merchants,
            fraud_rate=0,
            as_of=config.as_of,
        )
    generate_bank(output, config, include_defects=include_defects)
    st.session_state.active_run = str(output)
    return output


with st.sidebar:
    st.subheader("Generation controls")
    st.number_input("Seed", min_value=1, value=20260820, key="seed")
    st.number_input("Customers", min_value=1, max_value=10000, value=100, key="customers")
    st.number_input("Transactions", min_value=0, max_value=100000, value=500, key="transactions")
    st.number_input("Merchants", min_value=1, max_value=5000, value=50, key="merchants")
    st.slider("Fraud label rate", min_value=0.0, max_value=0.5, value=0.06, step=0.01, key="fraud_rate")
    st.text_input("Simulation time (ISO 8601)", value="2026-08-20T12:00:00+00:00", key="as_of")
    st.divider()
    st.caption("All data is synthetic. No AWS resources are used in V0.")

title_col, flow_col = st.columns([5, 1])
with title_col:
    st.title("Project MAX — V0: The Dirty Bank")
    st.caption("Meridian Bank operational source-system simulator")
with flow_col:
    st.write("")
    if st.button("View System Flow", type="primary", width="stretch"):
        system_flow_dialog()

st.markdown(
    '<div class="max-note"><strong>V0 boundary:</strong> these are independent operational sources and raw artifacts. There is no data lake, streaming platform, curated layer or machine learning model yet.</div>',
    unsafe_allow_html=True,
)

st.subheader("Generate source activity")
customer_col, transaction_col, fraud_col, dirty_col = st.columns(4)
try:
    with customer_col:
        if st.button("Generate customers", width="stretch"):
            path = create_run("customers")
            st.success(f"Created {path.name}")
    with transaction_col:
        if st.button("Generate transactions", width="stretch"):
            path = create_run("transactions")
            st.success(f"Created {path.name}")
    with fraud_col:
        if st.button("Generate fraud", width="stretch"):
            path = create_run("fraud", fraud_only=True)
            st.success(f"Created {path.name}")
    with dirty_col:
        if st.button("Create bad records", width="stretch"):
            path = create_run("dirty", include_defects=True)
            st.success(f"Created {path.name}")
except (ValueError, FileExistsError) as error:
    st.error(str(error))

runs = list_runs(RUNS_ROOT)
sample_run = REPOSITORY_ROOT / "source-systems" / "sample-data" / "v0-demo"
if sample_run.joinpath("manifest.json").exists():
    runs.append(sample_run)

st.divider()
st.subheader("Inspect source systems")
if not runs:
    st.info("Generate a source run to begin inspection.")
    st.stop()

run_labels = {str(path): path for path in runs}
default_run = st.session_state.get("active_run", str(runs[0]))
selected_key = st.selectbox(
    "Source run",
    options=list(run_labels),
    index=list(run_labels).index(default_run) if default_run in run_labels else 0,
    format_func=lambda value: Path(value).name,
)
selected_run = run_labels[selected_key]
manifest = load_manifest(selected_run)

counts = manifest["counts"]
metric_cols = st.columns(6)
for column, label, key in zip(
    metric_cols,
    ["Customers", "Accounts", "Payments", "Fraud labels", "Documents", "Defects"],
    ["customers", "accounts", "payments", "fraud_labels", "documents", "defects"],
    strict=True,
):
    column.metric(label, f"{counts.get(key, 0):,}")

files = list_source_files(selected_run)
relative = [str(path.relative_to(selected_run)) for path in files]
chosen_relative = st.selectbox("Source artifact", relative)
chosen = selected_run / chosen_relative
kind, preview = preview_file(chosen)
st.caption(f"{chosen_relative} · {chosen.stat().st_size:,} bytes")
if kind == "table":
    st.dataframe(pd.DataFrame(preview), width="stretch", hide_index=True)
elif kind == "json":
    st.json(preview)
elif kind == "text":
    st.code(preview)
else:
    st.info(f"Binary document: {preview['format']}. It is preserved for later document processing.")

with st.expander("Run manifest"):
    st.json(manifest)
