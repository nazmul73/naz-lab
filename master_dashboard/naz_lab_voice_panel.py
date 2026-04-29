"""Reusable Voice panel for Naz Lab."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from master_dashboard.naz_lab_nav import render_nav
from voice_workstation.voice_backend import (
    attach_audio_to_voice_job,
    create_voice_job,
    get_voice_config,
    list_voice_jobs,
    list_voice_outputs,
    save_voice_config,
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
    st.info("Voice job/output workflow is active. Real TTS engine is optional and can be connected through the Engine Config tab.")


def render_engine_config() -> None:
    st.markdown("### Engine Config")
    config = get_voice_config()
    st.warning("Keep engine_enabled=false until a real TTS engine has been selected and tested. The Drive-backed voice job workflow works without a real engine.")
    with st.form("voice_engine_config_form"):
        engine_enabled = st.checkbox("Enable real TTS engine", value=bool(config.get("engine_enabled", False)))
        engine_name = st.text_input("Engine name", value=str(config.get("engine_name", "pending_selection")))
        engine_command = st.text_input("Engine command/path", value=str(config.get("engine_command", "")), help="Example later: python /content/tts/run.py --input {input} --output {output}")
        output_extension = st.selectbox("Output extension", [".wav", ".mp3", ".m4a", ".ogg", ".flac"], index=[".wav", ".mp3", ".m4a", ".ogg", ".flac"].index(str(config.get("output_extension", ".wav"))) if str(config.get("output_extension", ".wav")) in [".wav", ".mp3", ".m4a", ".ogg", ".flac"] else 0)
        notes = st.text_area("Notes", value=str(config.get("notes", "")), height=100)
        submitted = st.form_submit_button("Save voice engine config")
    if submitted:
        saved = save_voice_config({
            "engine_enabled": engine_enabled,
            "engine_name": engine_name.strip() or "pending_selection",
            "engine_command": engine_command.strip(),
            "output_extension": output_extension,
            "notes": notes,
        })
        st.success("Voice engine config saved")
        st.json(saved)
    else:
        st.json(config)


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
    st.write("Create text-to-voice jobs, inspect audio outputs, attach existing audio files, and configure a future TTS engine from inside Naz Lab.")
    selected = render_nav(["Runtime", "Engine Config", "Create Job", "Jobs", "Outputs", "Attach Audio"], key="voice_sub", variant="sub")
    if selected == "Runtime":
        render_runtime()
    elif selected == "Engine Config":
        render_engine_config()
    elif selected == "Create Job":
        render_create_job()
    elif selected == "Jobs":
        render_jobs()
    elif selected == "Outputs":
        render_outputs()
    elif selected == "Attach Audio":
        render_attach_audio()
