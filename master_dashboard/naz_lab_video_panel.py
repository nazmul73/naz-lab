"""Planning-only Video panel for Naz Lab.

Video generation stays deferred/locked per Working Plan v2.0.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from shared.drive_paths import VIDEO_JOBS, VIDEO_OUTPUTS


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def render_video_panel() -> None:
    st.subheader("Video")
    st.warning("Video generation is deferred/locked for Naz Lab v1. This panel is planning-only.")

    c1, c2 = st.columns(2)
    c1.metric("Video jobs", _count_files(VIDEO_JOBS))
    c2.metric("Video outputs", _count_files(VIDEO_OUTPUTS))

    st.markdown("### Future flow")
    st.code(
        "script -> scene plan -> image prompts -> generated images -> voice -> video manifest -> rendered video later",
        language="text",
    )

    st.markdown("### Scene manifest placeholder")
    st.text_area(
        "Draft scene manifest",
        value="Scene 1: Hook\nScene 2: Context\nScene 3: Core story\nScene 4: CTA",
        height=180,
        key="naz_video_scene_manifest_placeholder",
    )
    st.button("Generate MP4", disabled=True, help="Locked until real video backend is explicitly enabled later.")
