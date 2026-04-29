"""Reusable Text Workstation panel for the Naz Lab dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from master_dashboard.naz_lab_nav import render_nav
from shared.drive_paths import IMAGE_JOBS, IMAGE_PROMPTS, SCRIPT_OUTPUTS, TEXT_OUTPUTS
from shared.job_queue_schema import read_json
from text_workstation.app_phase110 import (
    AVAILABLE_MODELS,
    CPU_RECOMMENDED_MODEL,
    MODE_CONFIG,
    call_ollama,
    create_image_job,
    ensure_dirs as ensure_text_dirs,
    installed_model_names,
    model_installed,
    needs_safe_bangla,
    save_text_output,
    template_output,
    template_prompt,
    user_requested_bangla,
)

TEXT_EXTENSIONS = {".txt", ".md", ".json"}
JSON_EXTENSIONS = {".json"}
AUTO_SAVE_MODES = {"Story Writer", "Viral Script Writer"}


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def latest_files(path: Path, extensions: set[str] | None = None, limit: int = 50) -> list[Path]:
    if not path.exists():
        return []
    files = [item for item in path.rglob("*") if item.is_file()]
    if extensions:
        files = [item for item in files if item.suffix.lower() in extensions]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def safe_json(path: Path, default: Any) -> Any:
    try:
        return read_json(path, default)
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}


def safe_text(path: Path, limit: int = 7000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception as exc:
        return f"Could not read {path}: {exc}"


def file_rows(path: Path, extensions: set[str] | None = None, limit: int = 50) -> list[dict[str, Any]]:
    rows = []
    for item in latest_files(path, extensions=extensions, limit=limit):
        rows.append({"Name": item.name, "Path": str(item), "Size KB": round(item.stat().st_size / 1024, 1)})
    return rows


def init_state() -> None:
    defaults = {
        "naz_text_output": "",
        "naz_text_saved_path": "",
        "naz_text_engine_status": "",
        "naz_text_last_job_path": "",
        "naz_text_last_mode": "",
        "naz_text_last_project": "",
        "naz_text_last_language": "",
        "naz_text_last_topic": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_builder() -> None:
    ensure_text_dirs()
    init_state()
    st.markdown("### Text Builder")
    c1, c2, c3 = st.columns(3)
    with c1:
        project = st.selectbox("Project", ["General Bangla", "True Noir Tales", "ToolFlow", "Custom"], index=0, key="naz_text_project")
        mode_options = list(MODE_CONFIG.keys()) + ["General Chat", "YouTube Script"]
        mode = st.selectbox("Mode", mode_options, index=0, key="naz_text_mode")
    with c2:
        language = st.selectbox("Language", ["Bangla", "English", "Mixed Bangla-English"], index=0, key="naz_text_language")
        model = st.selectbox("Model", AVAILABLE_MODELS, index=0, key="naz_text_model")
    with c3:
        length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1, key="naz_text_length")
        bangla_safe_mode = st.checkbox("Bangla Safe Mode", value=True, key="naz_text_safe")

    topic = st.text_area("Topic / input", value="একজন ছোট ব্যবসায়ী AI tools ব্যবহার করে প্রতিদিনের content planning সহজ করে ফেলল।", height=135, key="naz_text_topic")
    style = st.selectbox("Style preset", ["Default", "Simple Bangla", "True Noir Tales", "ToolFlow", "Custom"], index=0, key="naz_text_style")
    template_first = st.checkbox("Template-first for stable Bangla output", value=True, key="naz_text_template_first")

    b1, b2, b3 = st.columns(3)
    generate = b1.button("Generate", type="primary", use_container_width=True, key="naz_text_generate")
    save = b2.button("Save current output", use_container_width=True, key="naz_text_save")
    send_image = b3.button("Send to Image Job", use_container_width=True, key="naz_text_send_image")

    internal_mode = "Free Writer" if mode in ["General Chat", "YouTube Script"] else mode
    enriched_topic = topic if style == "Default" else f"Style preset: {style}\n\n{topic}"

    st.caption("Generate করলে output নিচে দেখা যাবে। Story Writer ও Viral Script Writer auto-save হবে; অন্য mode-এ প্রয়োজন হলে Save চাপুন।")

    if generate:
        if template_first and user_requested_bangla(enriched_topic, language):
            result = template_output(internal_mode, enriched_topic)
            engine_status = "naz_lab_template_first"
        else:
            try:
                with st.spinner(f"Generating with {model}..."):
                    result = call_ollama(enriched_topic, model, internal_mode, language, length, bangla_safe_mode)
                engine_status = f"ollama:{model}"
                if needs_safe_bangla(enriched_topic, language, result, bangla_safe_mode):
                    result = template_output(internal_mode, enriched_topic)
                    engine_status = f"bangla_safe_template_after_low_quality_model:{model}"
                    st.warning("Model output failed Bangla quality guard. Safe Bangla template was used.")
            except Exception as exc:
                result = template_output(internal_mode, enriched_topic)
                engine_status = f"template_after_error:{type(exc).__name__}"
                st.warning(f"Model generation failed. Safe template output was used. Error: {exc}")
        st.session_state.naz_text_output = result
        st.session_state.naz_text_engine_status = engine_status
        st.session_state.naz_text_last_mode = internal_mode
        st.session_state.naz_text_last_project = project
        st.session_state.naz_text_last_language = language
        st.session_state.naz_text_last_topic = enriched_topic
        st.session_state.naz_text_saved_path = ""
        if internal_mode in AUTO_SAVE_MODES:
            saved_path = save_text_output(internal_mode, project, language, enriched_topic, result, engine_status)
            st.session_state.naz_text_saved_path = str(saved_path)
            st.success(f"Generated, displayed, and auto-saved for workflow: {saved_path}")
        else:
            st.success("Generated. Output is displayed below. Not auto-saved; press Save current output only if needed.")

    output_text = st.text_area("Output", value=st.session_state.naz_text_output, height=360, key="naz_text_output_area")
    st.session_state.naz_text_output = output_text
    if st.session_state.naz_text_engine_status:
        st.caption(f"Engine status: {st.session_state.naz_text_engine_status}")
    if st.session_state.naz_text_saved_path:
        st.success(f"Last saved: {st.session_state.naz_text_saved_path}")
    if st.session_state.naz_text_last_job_path:
        st.info(f"Last image job: {st.session_state.naz_text_last_job_path}")

    save_mode = st.session_state.naz_text_last_mode or internal_mode
    save_project = st.session_state.naz_text_last_project or project
    save_language = st.session_state.naz_text_last_language or language
    save_topic = st.session_state.naz_text_last_topic or enriched_topic

    if save:
        if not output_text.strip():
            st.error("No output to save.")
        else:
            saved_path = save_text_output(save_mode, save_project, save_language, save_topic, output_text, st.session_state.naz_text_engine_status or "manual_save")
            st.session_state.naz_text_saved_path = str(saved_path)
            st.success(f"Saved: {saved_path}")

    if send_image:
        if not output_text.strip():
            st.error("No output to send.")
        else:
            source = Path(st.session_state.naz_text_saved_path) if st.session_state.naz_text_saved_path else None
            image_prompt = output_text if save_mode == "Prompt Improver" else template_prompt(save_topic + "\n" + output_text[:500])
            job_path = create_image_job(save_project, save_mode, save_topic, image_prompt, source)
            st.session_state.naz_text_last_job_path = str(job_path)
            st.success(f"Image job created: {job_path}")
            st.json(safe_json(job_path, {}))


def render_library_section(folder: Path, ext: set[str], label: str) -> None:
    st.markdown(f"### {label}")
    rows = file_rows(folder, ext)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        selected = st.selectbox("Preview file", [row["Path"] for row in rows], key=f"text_library_{folder.name}_{label}")
        selected_path = Path(selected)
        if selected_path.suffix.lower() == ".json":
            st.json(safe_json(selected_path, {}))
        else:
            st.text_area("Preview", safe_text(selected_path), height=320, key=f"preview_{folder.name}_{label}")
    else:
        st.info(f"No files found in {folder}")


def render_library() -> None:
    st.markdown("### Text Output Library")
    selected = render_nav(["Text outputs", "Scripts", "Image prompts", "Image jobs"], key="text_library_sub", variant="sub")
    mapping = {
        "Text outputs": (TEXT_OUTPUTS, TEXT_EXTENSIONS),
        "Scripts": (SCRIPT_OUTPUTS, TEXT_EXTENSIONS),
        "Image prompts": (IMAGE_PROMPTS, TEXT_EXTENSIONS),
        "Image jobs": (IMAGE_JOBS, JSON_EXTENSIONS),
    }
    folder, ext = mapping[selected]
    render_library_section(folder, ext, selected)


def render_status() -> None:
    st.markdown("### Backend Status")
    model = st.selectbox("Check model", AVAILABLE_MODELS, index=0, key="naz_text_check_model")
    names = installed_model_names()
    c1, c2, c3 = st.columns(3)
    c1.metric("Phase", "Text merged")
    c2.metric("Selected model installed", "yes" if model_installed(model) else "no")
    c3.metric("Installed models", len(names))
    st.json({"recommended_cpu_model": CPU_RECOMMENDED_MODEL, "selected_model": model, "installed_models": names, "text_outputs": str(TEXT_OUTPUTS), "script_outputs": str(SCRIPT_OUTPUTS), "image_prompts": str(IMAGE_PROMPTS), "image_jobs": str(IMAGE_JOBS), "bangla_safe_mode": "available/default on", "auto_save_modes": sorted(AUTO_SAVE_MODES)})


def render_text_panel() -> None:
    st.subheader("Text Workstation")
    st.write("Generate scripts, stories, captions, free writing, and image prompts directly from Naz Lab. Save outputs and send prompts into the Image Job Queue.")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Text outputs", count_files(TEXT_OUTPUTS))
    col_b.metric("Script outputs", count_files(SCRIPT_OUTPUTS))
    col_c.metric("Image prompts", count_files(IMAGE_PROMPTS))
    col_d.metric("Image jobs", count_files(IMAGE_JOBS))
    selected = render_nav(["Create", "Library", "Backend Status"], key="text_sub", variant="sub")
    if selected == "Create":
        render_builder()
    elif selected == "Library":
        render_library()
    elif selected == "Backend Status":
        render_status()
