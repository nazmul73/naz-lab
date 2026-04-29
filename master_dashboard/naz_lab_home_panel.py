"""Home panel for the Naz Lab dashboard.

Working Plan v2.0 overview and quick operator guidance.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from shared.drive_paths import BASE_PATH, IMAGE_JOBS, TEXT_OUTPUTS, VOICE_JOBS


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def render_home_panel() -> None:
    st.subheader("Home")
    st.write("Naz Lab is the unified command center for content creation, review, and manual-gated publishing workflows.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Drive base", "ready" if BASE_PATH.exists() else "pending")
    c2.metric("Text outputs", _count_files(TEXT_OUTPUTS))
    c3.metric("Image jobs", _count_files(IMAGE_JOBS))
    c4.metric("Voice jobs", _count_files(VOICE_JOBS))

    st.markdown("### Quick actions")
    st.info("Use Text to generate content, create image jobs, send voice jobs, and draft review packages.")
    st.info("Use Image for queue/gallery workflows, Voice for consent-gated audio workflow, and Facebook Post for dry-run/manual-gated handoff.")
    st.warning("Video generation is deferred/locked in v1. This dashboard keeps a planning-only Video tab.")

    st.markdown("### Working Plan v2.0 rules")
    for rule in [
        "No Complete Package tab.",
        "Real Facebook posting remains disabled/manual-gated.",
        "Video generation remains deferred.",
        "Default negative prompt stays lightweight: no fake logo, no watermark, no distorted face.",
    ]:
        st.checkbox(rule, value=True, disabled=True)
