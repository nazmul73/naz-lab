"""Reusable Voice panel for Naz Lab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from voice_workstation.voice_backend import (
    attach_audio_to_voice_job,
    create_voice_job,
    list_voice_jobs,
    list_voice_outputs,
    summarize_voice_job,
    voice_runtime_status,
)
from shared.job_queue_schema import read_json

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}


def render_runtime() -> None:
    st.markdown("### Voice Runtime")
    status = voice_runtime_status()
    c1, c2, c3 = st.columns(3)
    c1.metric("Voice jobs", status.get("voice_jobs", 0))
    c2.metric("Voice outputs", status.get("voice_outputs", 0))
    c3.metric("TTS engine", "connected" if status.get("tts_engine_connected") else "pending")
    st.json(status)
    st.info("Voice job/output workflow is active. Real TTS engine connection remains pending unless an external backend is provided.")


def render_create_job() -> None:
    st.markdown("### Create text-to-voice job")
    project = st.selectbox("Project", ["General Bangla", "True Noir Tales", "ToolFlow", "Custom"], index=0, key="voice_project")
    topic = st.text_input("Topic", value="Naz Lab voice narration", key="voice_topic")
    language = st.selectbox("Language", ["Bangla", "English", "Mixed Bangla-English"], index=0, key="voice_language")
    preset = st.selectbox("Voice preset", ["Default", "Bangla narration", "English narration", "Custom"], index=0, key="voice_preset")
    text = st.text_area("Narration text", value="", height=180, placeholder="Paste or write narration text here...", key="voice_input_text")
    source_text_path = st.text_input("Source text path optional", value="", key="voice_source_text_path")
    if st.button("Create voice job", type="primary", key="voice_create_job"):
        if not text.strip():
            st.error("Narration text is required.")
        else:
            path = create_voice_job(project=project, topic=topic, text=text, voice_preset=preset, language=language, source_text_path=source_text_path)
            st.success(f"Voice job created: {path}")
            st.json(read_json(path, {}))


def render_jobs() -> None:
    st.markdown("### Voice Jobs")
    jobs = list_voice_jobs()
    if not jobs:
        st.info("No voice jobs yet.")
        return
    rows = [summarize_voice_job(path) for path in jobs]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open voice job", [str(path) for path in jobs], key="voice_open_job"))
    record = read_json(selected, {})
    st.json(record)
    audio_path = record.get("output_audio_path", "") if isinstance(record, dict) else ""
    if audio_path and Path(audio_path).exists():
        st.audio(audio_path)


def render_outputs() -> None:
    st.markdown("### Voice Outputs")
    outputs = list_voice_outputs()
    if not outputs:
        st.info("No audio outputs found. Put generated audio files under /content/drive/MyDrive/NazLab/voice_outputs/ to preview them here.")
        return
    rows = [{"Name": path.name, "Path": str(path), "Size KB": round(path.stat().st_size / 1024, 1)} for path in outputs]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open audio output", [str(path) for path in outputs], key="voice_open_audio"))
    st.audio(str(selected))
    st.download_button("Download audio", data=selected.read_bytes(), file_name=selected.name, key="voice_download_audio")


def render_attach_audio() -> None:
    st.markdown("### Attach existing audio to voice job")
    jobs = list_voice_jobs()
    outputs = list_voice_outputs()
    if not jobs:
        st.info("Create a voice job first.")
        return
    if not outputs:
        st.info("No audio outputs found to attach.")
        return
    job_path = st.selectbox("Voice job", [str(path) for path in jobs], key="voice_attach_job")
    audio_path = st.selectbox("Audio output", [str(path) for path in outputs], key="voice_attach_audio")
    if st.button("Attach audio to job", key="voice_attach_button"):
        result = attach_audio_to_voice_job(job_path, audio_path)
        st.json(result)


def render_voice_panel() -> None:
    st.subheader("Voice / Text-to-Voice")
    st.write("Create text-to-voice jobs, inspect audio outputs, and attach existing audio files from inside Naz Lab. Real TTS engine connection can be added later.")
    tabs = st.tabs(["Runtime", "Create Job", "Jobs", "Outputs", "Attach Audio"])
    with tabs[0]:
        render_runtime()
    with tabs[1]:
        render_create_job()
    with tabs[2]:
        render_jobs()
    with tabs[3]:
        render_outputs()
    with tabs[4]:
        render_attach_audio()
