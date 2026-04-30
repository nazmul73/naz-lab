"""Naz Lab dashboard v12 compatibility hub.

Working Plan v2.0 routes dashboard tabs to the canonical panel functions. This
file stays available for compatibility, while app_official.py uses app_main.py
as the official launcher path.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from master_dashboard.naz_lab_facebook_panel import render_facebook_panel  # noqa: E402
from master_dashboard.naz_lab_files_panel import render_files_panel  # noqa: E402
from master_dashboard.naz_lab_health_panel import render_health_panel  # noqa: E402
from master_dashboard.naz_lab_home_panel import render_home_panel  # noqa: E402
from master_dashboard.naz_lab_image_panel import render_image_panel  # noqa: E402
from master_dashboard.naz_lab_nav import render_nav  # noqa: E402
from master_dashboard.naz_lab_runbook_panel import render_runbook_panel  # noqa: E402
from master_dashboard.naz_lab_text_panel import render_text_panel  # noqa: E402
from master_dashboard.naz_lab_video_panel import render_video_panel  # noqa: E402
from master_dashboard.naz_lab_voice_panel import render_voice_panel  # noqa: E402
from shared.drive_paths import WORKSTATION_LINKS_JSON  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402

PHASE = "naz-lab-dashboard-v12-working-plan-v2.0-compatible"
STATUS = "completion-v1.1-panel-routing-fixed"
HEALTH_TAB = "Health / Logs"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def render_css() -> None:
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.1rem; padding-bottom: 2rem; }
          .naz-hero {
            padding: 1.35rem 1.5rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 52%, #334155 100%);
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.18);
          }
          .naz-hero h1 { margin: 0; font-size: 2.25rem; letter-spacing: -0.04em; }
          .naz-hero p { margin: 0.45rem 0 0 0; opacity: 0.92; font-size: 1.02rem; }
          .naz-main-menu-shell, .naz-sub-menu-shell {
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 0.55rem;
            margin-bottom: 1rem;
            background: #f8fafc;
          }
          .naz-section-body { border-top: 1px solid #e5e7eb; padding-top: 1rem; margin-top: 0.35rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    update_workstation_status(WORKSTATION_LINKS_JSON, "naz_lab", {"status": STATUS, "phase": PHASE, "last_seen": now_iso()})
    st.markdown(
        f"""
        <div class="naz-hero">
          <h1>Naz Lab</h1>
          <p>Unified AI workstation command center for Text, Voice, Image, planning-only Video, Facebook handoff, Files, Health / Logs, and Runbook. Phase: {PHASE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Naz Lab", page_icon="🧪", layout="wide")
    render_css()
    render_header()
    options = ["Home", "Text", "Voice", "Image", "Video", "Facebook Post", "Files", HEALTH_TAB, "Runbook"]
    selected = render_nav(options, key="main", variant="main")
    st.markdown('<div class="naz-section-body">', unsafe_allow_html=True)
    if selected == "Home":
        render_home_panel()
    elif selected == "Text":
        render_text_panel()
    elif selected == "Voice":
        render_voice_panel()
    elif selected == "Image":
        render_image_panel()
    elif selected == "Video":
        render_video_panel()
    elif selected == "Facebook Post":
        render_facebook_panel()
    elif selected == "Files":
        render_files_panel()
    elif selected == HEALTH_TAB:
        render_health_panel()
    elif selected == "Runbook":
        render_runbook_panel()
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
