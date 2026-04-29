"""Runbook panel for Naz Lab Working Plan v2.0."""

from __future__ import annotations

import streamlit as st


def render_runbook_panel() -> None:
    st.subheader("Runbook")
    st.markdown("### Operator rules")
    for rule in [
        "Run one Streamlit app only on port 8502 in normal Colab runtime.",
        "Use app_official.py as the official launcher target.",
        "Use Home, Text, Voice, Image, Video, Facebook Post, Files, Health/Logs, and Runbook tabs.",
        "Do not add a Complete Package tab.",
        "Keep real Facebook posting disabled/manual-gated until explicitly approved.",
        "Keep video generation deferred/locked for v1.",
        "Keep heavy image/video dependencies out of lightweight Colab runtime unless real backend is explicitly enabled.",
    ]:
        st.checkbox(rule, value=True, disabled=True)

    st.markdown("### Colab launcher target")
    st.code(
        "python -m streamlit run /content/naz-lab/master_dashboard/app_official.py --server.port 8502 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false",
        language="bash",
    )

    st.markdown("### Runtime error log")
    st.code('print(open("/content/streamlit_naz_lab_runtime.log").read()[-4000:])', language="python")

    st.markdown("### Colab verification checklist")
    checklist = [
        "Dashboard opens.",
        "Main menu same-window works.",
        "Text > Create opens.",
        "Casual chat: how are you? returns English casual reply, not Bangla business template.",
        "Backend Status shows shared.ollama_text_generation.call_ollama and shared.text_workstation_helpers.",
        "Prompt Improver creates output, metadata, and image job.",
        "Text Library shows Chat sessions / Image jobs / Text metadata.",
        "Voice reference audio save requires consent checkbox.",
        "Image reference upload is visible.",
        "Facebook Post safe config is visible.",
        "No Complete Package tab.",
    ]
    for item in checklist:
        st.checkbox(item, value=False, key=f"runbook_{item}")
