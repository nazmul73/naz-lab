"""Naz Lab Main Interface Hub.

A polished, lightweight Streamlit home app that interconnects the active Naz Lab
apps, launchers, notebooks, Drive folders, and workflow stages.

This app does not run heavy generation by itself. It is the command center for:
- Text Workstation
- Real Image Backend
- Final Content Package Flow
- Social Review / Facebook Gate
- Runbooks and launchers
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    TEXT_OUTPUTS,
    SCRIPT_OUTPUTS,
    IMAGE_PROMPTS,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    LOGS_DIR,
    WORKSTATION_LINKS_JSON,
)
from shared.job_queue_schema import read_json  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402

PHASE = "main-hub-1.0"
STATUS = "official-main-interface-ready"

APP_CARDS = [
    {
        "name": "Text Workstation",
        "status": "PASS",
        "app": "text_workstation/app_official.py",
        "port": "8501",
        "purpose": "Bangla-first text, script, caption, prompt, and image-job creation.",
        "runtime": "CPU/GPU, Ollama required",
    },
    {
        "name": "Final Package Flow",
        "status": "READY / runtime pending",
        "app": "master_dashboard/app_phase222.py",
        "port": "8502",
        "purpose": "Auto/manual/reference packages, preview, approve, export.",
        "runtime": "CPU OK; no GPU needed unless generating images",
    },
    {
        "name": "Real Image Backend",
        "status": "GPU PASS",
        "app": "master_dashboard/app_phase221.py",
        "port": "8502",
        "purpose": "Generate PNG images from image jobs with Diffusers on Colab GPU.",
        "runtime": "GPU required for generation",
    },
    {
        "name": "Unified Dashboard",
        "status": "READY / runtime pending",
        "app": "master_dashboard/app_phase220.py",
        "port": "8502",
        "purpose": "Jobs, image manifests, social review, health, package preview in one dashboard.",
        "runtime": "CPU OK",
    },
    {
        "name": "Social Review + Facebook Gate",
        "status": "SAFE / gated",
        "app": "master_dashboard/app_phase219.py",
        "port": "8502",
        "purpose": "Manual gate, dry-run log, disabled-by-default Facebook config.",
        "runtime": "CPU OK; real API only after explicit setup",
    },
]

LAUNCHERS = [
    {
        "name": "All-in-one official launcher",
        "path": "launchers/naz_lab_all_in_one_colab.py",
        "target": "master_dashboard/app_official.py",
        "note": "Default main launcher for current official dashboard.",
    },
    {
        "name": "Text Workstation launcher",
        "path": "launchers/phase1_10_text_workstation_colab.py",
        "target": "text_workstation/app_phase110.py",
        "note": "Use when testing text output and image job creation.",
    },
    {
        "name": "Real Image Backend launcher",
        "path": "launchers/phase3_1_real_image_backend_colab.py",
        "target": "master_dashboard/app_phase221.py",
        "note": "Use only with Colab GPU for real image generation.",
    },
]

NOTEBOOK_FLOW = [
    {
        "step": "1",
        "name": "Foundation / repo loader",
        "notebook_or_launcher": "launchers/naz_lab_all_in_one_colab.py",
        "output": "Repo, Drive folders, official dashboard",
    },
    {
        "step": "2",
        "name": "Text Workstation",
        "notebook_or_launcher": "launchers/phase1_10_text_workstation_colab.py",
        "output": "text_outputs + image_job JSON",
    },
    {
        "step": "3",
        "name": "Real Image Backend",
        "notebook_or_launcher": "launchers/phase3_1_real_image_backend_colab.py",
        "output": "PNG + metadata JSON + updated job JSON",
    },
    {
        "step": "4",
        "name": "Final Package Flow",
        "notebook_or_launcher": "master_dashboard/app_phase222.py",
        "output": "final package JSON + approved/exported packages",
    },
    {
        "step": "5",
        "name": "Social Review / Facebook Gate",
        "notebook_or_launcher": "master_dashboard/app_phase219.py",
        "output": "dry-run/manual-gated social posting candidate",
    },
]

DRIVE_FOLDERS = [
    ("Text outputs", TEXT_OUTPUTS),
    ("Script outputs", SCRIPT_OUTPUTS),
    ("Image prompts", IMAGE_PROMPTS),
    ("Image jobs", IMAGE_JOBS),
    ("Image outputs", IMAGE_OUTPUTS),
    ("Logs", LOGS_DIR),
    ("Final packages", BASE_PATH / "final_packages"),
    ("Reference images", BASE_PATH / "reference_images"),
]


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def safe_json(path: Path, default: Any) -> Any:
    try:
        return read_json(path, default)
    except Exception:
        return default


def render_header() -> None:
    update_workstation_status(WORKSTATION_LINKS_JSON, "main_interface", {"status": STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    st.markdown(
        """
        <div style="padding: 1.2rem 1.4rem; border-radius: 22px; background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #374151 100%); color: white; margin-bottom: 1rem;">
          <h1 style="margin:0; font-size:2.1rem;">Naz Lab AI Ecosystem</h1>
          <p style="margin:0.35rem 0 0 0; font-size:1.02rem; opacity:0.9;">Official Main Interface Hub — text, image, package, review, and launcher map</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_cards() -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Text Workstation", "PASS")
    c2.metric("Real Image", "GPU PASS")
    c3.metric("Packages", "READY")
    c4.metric("Facebook", "GATED")


def render_app_cards() -> None:
    st.subheader("Active Workstations")
    for card in APP_CARDS:
        with st.container(border=True):
            c1, c2, c3 = st.columns([2.4, 1.2, 1.7])
            c1.markdown(f"### {card['name']}")
            c1.write(card["purpose"])
            c2.metric("Status", card["status"])
            c3.code(f"{card['app']}\nport {card['port']}")
            c3.caption(card["runtime"])


def render_workflow() -> None:
    st.subheader("Notebook / Launcher Interconnect Flow")
    st.dataframe(NOTEBOOK_FLOW, use_container_width=True, hide_index=True)
    st.markdown(
        """
```text
Text Workstation -> Image Job JSON -> Real Image Backend -> Final Package Flow -> Social Review -> Facebook Gate
```
"""
    )


def render_drive_map() -> None:
    st.subheader("Drive Folder Map")
    rows = [{"Folder": label, "Path": str(path), "Files": count_files(path), "Status": "ready" if path.exists() else "missing"} for label, path in DRIVE_FOLDERS]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_launchers() -> None:
    st.subheader("Launchers")
    st.dataframe(LAUNCHERS, use_container_width=True, hide_index=True)
    st.markdown("### Colab quick commands")
    st.code(
        """# Official main app
%run /content/naz-lab/launchers/naz_lab_all_in_one_colab.py

# Real Image Backend GPU app
%run /content/naz-lab/launchers/phase3_1_real_image_backend_colab.py
""",
        language="python",
    )


def render_current_files() -> None:
    st.subheader("Current JSON State")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Workstation links")
        st.json(safe_json(WORKSTATION_LINKS_JSON, {}))
    with col_b:
        package_index = BASE_PATH / "final_packages" / "package_index.json"
        st.markdown("#### Package index")
        st.json(safe_json(package_index, {"items": []}))


def render_runbook() -> None:
    st.subheader("Runbook Summary")
    st.info("Use the Text Workstation to create content and image jobs. Use the Real Image Backend with GPU only when generating images. Use Final Package Flow for packaging, preview, approval, and export.")
    st.warning("Facebook real posting is disabled by default and must remain manual-gated. Video generation remains deferred after v1.")
    checklist = [
        "Create or select text output",
        "Create image job JSON",
        "Generate image on GPU or attach existing image",
        "Build final package",
        "Preview package assets",
        "Approve or export package",
        "Use Social Review/Facebook Gate only in dry-run unless explicitly configured",
    ]
    for item in checklist:
        st.checkbox(item, value=True, disabled=True)


def main() -> None:
    st.set_page_config(page_title="Naz Lab Main Hub", page_icon="🧪", layout="wide")
    render_header()
    render_status_cards()
    tabs = st.tabs(["Workstations", "Flow", "Drive Map", "Launchers", "State", "Runbook"])
    with tabs[0]:
        render_app_cards()
    with tabs[1]:
        render_workflow()
    with tabs[2]:
        render_drive_map()
    with tabs[3]:
        render_launchers()
    with tabs[4]:
        render_current_files()
    with tabs[5]:
        render_runbook()


if __name__ == "__main__":
    main()
