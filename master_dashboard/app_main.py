"""Naz Lab official app hub.

Working Plan v2.0 dashboard wrapper. This file orchestrates the stable Naz Lab
same-window tabs without modifying app_official.py or naz_lab_dashboard_v12.py.
"""

from __future__ import annotations

import sys
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

PHASE = "working-plan-v2.0-missing-panels"


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
          .naz-menu-label { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; margin: 0.35rem 0; color: #2563eb; }
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
    st.markdown(
        f"""
        <div class="naz-hero">
          <h1>Naz Lab</h1>
          <p>Unified command center for Text, Voice, Image, planning-only Video, Facebook handoff, Files, Health/Logs, and Runbook. Phase: {PHASE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Naz Lab", page_icon="🧪", layout="wide")
    render_css()
    render_header()
    tabs = ["Home", "Text", "Voice", "Image", "Video", "Facebook Post", "Files", "Health/Logs", "Runbook"]
    selected = render_nav(tabs, key="main", variant="main")
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
    elif selected == "Health/Logs":
        render_health_panel()
    elif selected == "Runbook":
        render_runbook_panel()
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
