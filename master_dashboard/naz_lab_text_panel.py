"""Reusable Text Workstation panel for the Naz Lab dashboard.

Backend-ready Text Builder panel with:
- approved model policy only: gemma2:2b, qwen2.5:1.5b, qwen2.5:3b
- casual chat detection
- metadata sidecar save
- Prompt Improver automatic Image Job JSON handoff
- Drive-backed Ollama persistence status
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from master_dashboard.naz_lab_nav import render_nav
from shared.drive_paths import CHAT_OUTPUTS, IMAGE_JOBS, IMAGE_PROMPTS, SCRIPT_OUTPUTS, TEXT_METADATA, TEXT_OUTPUTS
from shared.job_queue_schema import read_json
from shared.model_policy import (
    ALLOWED_TEXT_MODELS,
    BLOCKED_TEXT_MODELS,
    MINIMUM_CPU_TEXT_MODEL,
    RECOMMENDED_TEXT_MODEL,
    blocked_model_reason,
    filter_allowed_text_models,
    model_policy_status,
    normalize_text_model,
)
from shared.ollama_persistence import ensure_ollama_persistence
from shared.text_pipeline import create_image_job_from_text, persist_text_result_and_optional_image_job
from text_workstation.app_phase110 import (
    MODE_CONFIG,
    call_ollama,
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
OUTPUT_AREA_BASE_KEY = "naz_text_output_area"
TEMPLATE_CHECKBOX_KEY = "naz_text_template_first"
AVAILABLE_MODELS = filter_allowed_text_models(ALLOWED_TEXT_MODELS)
CPU_RECOMMENDED_MODEL = MINIMUM_CPU_TEXT_MODEL

MODE_POLICY: dict[str, dict[str, Any]] = {
    "General Chat": {"internal_mode": "General Chat", "auto_save": False, "output_dir": CHAT_OUTPUTS, "template_default": False, "image_job": False},
    "Free Writer": {"internal_mode": "Free Writer", "auto_save": False, "output_dir": TEXT_OUTPUTS, "template_default": False, "image_job": True},
    "Story Writer": {"internal_mode": "Story Writer", "auto_save": True, "output_dir": TEXT_OUTPUTS, "template_default": True, "image_job": True},
    "Viral Script Writer": {"internal_mode": "Viral Script Writer", "auto_save": True, "output_dir": SCRIPT_OUTPUTS, "template_default": True, "image_job": True},
    "Caption Writer": {"internal_mode": "Caption Writer", "auto_save": False, "output_dir": TEXT_OUTPUTS, "template_default": True, "image_job": True},
    "Prompt Improver": {"internal_mode": "Prompt Improver", "auto_save": False, "output_dir": IMAGE_PROMPTS, "template_default": True, "image_job": True},
    "YouTube Script": {"internal_mode": "YouTube Script", "auto_save": False, "output_dir": SCRIPT_OUTPUTS, "template_default": True, "image_job": True},
}


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
    rows: list[dict[str, Any]] = []
    for item in latest_files(path, extensions=extensions, limit=limit):
        rows.append({"Name": item.name, "Path": str(item), "Size KB": round(item.stat().st_size / 1024, 1)})
    return rows


def get_mode_policy(mode: str) -> dict[str, Any]:
    return MODE_POLICY.get(mode, MODE_POLICY["Free Writer"])


def has_bangla(text: str) -> bool:
    return any("\u0980" <= ch <= "\u09FF" for ch in text)


def looks_like_casual_chat(text: str) -> bool:
    clean = " ".join(text.strip().lower().split())
    if not clean:
        return False
    chat_phrases = {
        "hi", "hello", "hey", "how are you", "how are you?", "who are you", "who are you?",
        "what are you", "what are you?", "thanks", "thank you", "ok", "okay", "test",
        "তুমি কেমন আছ", "তুমি কেমন আছো", "কেমন আছ", "কেমন আছো", "হাই", "হ্যালো",
    }
    if clean in chat_phrases:
        return True
    word_count = len(clean.replace("?", "").replace("।", "").split())
    return word_count <= 6 and (clean.endswith("?") or clean.endswith("？") or clean.endswith("।"))


def resolve_effective_mode_language(selected_mode: str, internal_mode: str, language: str, topic: str) -> tuple[str, str, str]:
    clean = topic.strip()
    effective_mode = internal_mode
    reason = "selected_mode"
    if selected_mode in ["General Chat", "Free Writer"] and looks_like_casual_chat(clean):
        effective_mode = "General Chat"
        reason = "casual_chat_detected"
    if not has_bangla(clean) and language != "English" and effective_mode in ["General Chat", "Free Writer"]:
        effective_language = "English"
    else:
        effective_language = language
    return effective_mode, effective_language, reason


def fallback_output(mode: str, topic: str, language: str) -> str:
    clean = " ".join(topic.strip().split())
    if mode == "General Chat" and not has_bangla(clean):
        lower = clean.lower().strip(" ?!.")
        if lower in ["hi", "hello", "hey"]:
            return "Hi! How can I help you today?"
        if lower == "how are you":
            return "I'm doing well, thanks for asking. How can I help you today?"
        if lower in ["who are you", "what are you"]:
            return "I'm Naz Lab's AI assistant inside this dashboard. I can help with text, scripts, prompts, image jobs, voice jobs, and content workflow."
        return f"I understand: {clean}\n\nHow would you like me to help with this?"
    return template_output(mode, topic)


def init_state() -> None:
    defaults = {
        "naz_text_output": "",
        "naz_text_output_version": 0,
        "naz_text_saved_path": "",
        "naz_text_last_metadata_path": "",
        "naz_text_engine_status": "",
        "naz_text_last_job_path": "",
        "naz_text_last_mode": "",
        "naz_text_last_project": "",
        "naz_text_last_language": "",
        "naz_text_last_topic": "",
        "naz_text_last_model": RECOMMENDED_TEXT_MODEL,
        "naz_text_pending_success": "",
        "naz_text_pending_warning": "",
        "naz_text_last_selected_mode": "Free Writer",
        TEMPLATE_CHECKBOX_KEY: False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sync_template_default_for_mode(mode: str) -> None:
    last_mode = st.session_state.get("naz_text_last_selected_mode")
    if last_mode != mode:
        st.session_state["naz_text_last_selected_mode"] = mode
        st.session_state[TEMPLATE_CHECKBOX_KEY] = bool(get_mode_policy(mode).get("template_default", False))


def output_area_key() -> str:
    return f"{OUTPUT_AREA_BASE_KEY}_{st.session_state.naz_text_output_version}"


def set_generated_output(result: str) -> None:
    st.session_state.naz_text_output = result
    st.session_state.naz_text_output_version += 1
    st.session_state[output_area_key()] = result


def get_current_output() -> str:
    widget_key = output_area_key()
    widget_value = st.session_state.get(widget_key, "")
    state_value = st.session_state.get("naz_text_output", "")
    return str(widget_value or state_value or "")


def render_pending_messages() -> None:
    if st.session_state.naz_text_pending_warning:
        st.warning(st.session_state.naz_text_pending_warning)
        st.session_state.naz_text_pending_warning = ""
    if st.session_state.naz_text_pending_success:
        st.success(st.session_state.naz_text_pending_success)
        st.session_state.naz_text_pending_success = ""


def persist_generated_text(
    *,
    mode: str,
    project: str,
    language: str,
    topic: str,
    model: str,
    engine_status: str,
    result: str,
    saved_path: str | Path | None,
    auto_image_job_for_prompt_improver: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, str]:
    return persist_text_result_and_optional_image_job(
        mode=mode,
        project=project,
        language=language,
        topic=topic,
        prompt=topic,
        model=model,
        engine_status=engine_status,
        output_text=result,
        output_text_path=saved_path,
        auto_image_job_for_prompt_improver=auto_image_job_for_prompt_improver,
        extra=extra or {},
    )


def render_builder() -> None:
    ensure_text_dirs()
    init_state()
    st.markdown("### Text Builder")
    mode_options = ["General Chat", "Free Writer", "Story Writer", "Viral Script Writer", "Caption Writer", "Prompt Improver", "YouTube Script"]
    c1, c2, c3 = st.columns(3)
    with c1:
        project = st.selectbox("Project", ["General Bangla", "True Noir Tales", "ToolFlow", "Custom"], index=0, key="naz_text_project")
        last = st.session_state.get("naz_text_last_selected_mode", "Free Writer")
        mode = st.selectbox("Mode", mode_options, index=mode_options.index(last) if last in mode_options else 1, key="naz_text_mode")
    sync_template_default_for_mode(mode)
    with c2:
        language = st.selectbox("Language", ["Bangla", "English", "Mixed Bangla-English"], index=0, key="naz_text_language")
        model = st.selectbox("Model", AVAILABLE_MODELS, index=0, key="naz_text_model")
    with c3:
        length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1, key="naz_text_length")
        bangla_safe_mode = st.checkbox("Bangla Safe Mode", value=True, key="naz_text_safe")

    safe_model = normalize_text_model(model)
    if safe_model != model:
        st.warning(blocked_model_reason(model))
        model = safe_model

    policy = get_mode_policy(mode)
    internal_mode = str(policy["internal_mode"])
    topic = st.text_area("Topic / input", value="", height=135, key="naz_text_topic", placeholder="Write or paste your topic/input here...")
    style = st.selectbox("Style preset", ["Default", "Simple Bangla", "True Noir Tales", "ToolFlow", "Custom"], index=0, key="naz_text_style")
    template_first = st.checkbox("Template-first / structured fallback", key=TEMPLATE_CHECKBOX_KEY, help="General Chat/Free Writer default OFF. Structured modes default ON.")

    b1, b2, b3 = st.columns(3)
    generate = b1.button("Generate", type="primary", use_container_width=True, key="naz_text_generate")
    save = b2.button("Save current output", use_container_width=True, key="naz_text_save")
    send_image = b3.button("Send to Image Job", use_container_width=True, key="naz_text_send_image")

    enriched_topic = topic if style == "Default" else f"Style preset: {style}\n\n{topic}"
    auto_save = bool(policy.get("auto_save", False))
    st.caption("Prompt Improver auto-exports image jobs. Text metadata is saved for every generation. Weak Bangla models are blocked by policy.")

    if generate:
        if not topic.strip():
            st.error("Topic / input is required.")
            return
        warnings: list[str] = []
        effective_mode, effective_language, effective_reason = resolve_effective_mode_language(mode, internal_mode, language, enriched_topic)
        if effective_reason == "casual_chat_detected" and mode != "General Chat":
            warnings.append("Short conversational input detected; handled as General Chat instead of content template.")
        if template_first and user_requested_bangla(enriched_topic, effective_language):
            result = fallback_output(effective_mode, enriched_topic, effective_language)
            engine_status = "naz_lab_template_first"
        else:
            try:
                with st.spinner(f"Generating with {model}..."):
                    result = call_ollama(enriched_topic, model, effective_mode, effective_language, length, bangla_safe_mode)
                engine_status = f"ollama:{model}"
                if needs_safe_bangla(enriched_topic, effective_language, result, bangla_safe_mode):
                    result = fallback_output(effective_mode, enriched_topic, effective_language)
                    engine_status = f"fallback_after_low_quality_model:{model}"
                    warnings.append("Model output failed quality guard. Safe fallback was used.")
            except Exception as exc:
                result = fallback_output(effective_mode, enriched_topic, effective_language)
                engine_status = f"fallback_after_error:{type(exc).__name__}"
                warnings.append(f"Model generation failed. Safe fallback was used. Error: {exc}")

        set_generated_output(result)
        st.session_state.naz_text_engine_status = engine_status
        st.session_state.naz_text_last_mode = effective_mode
        st.session_state.naz_text_last_project = project
        st.session_state.naz_text_last_language = effective_language
        st.session_state.naz_text_last_topic = enriched_topic
        st.session_state.naz_text_last_model = model
        st.session_state.naz_text_saved_path = ""
        st.session_state.naz_text_last_metadata_path = ""
        st.session_state.naz_text_last_job_path = ""

        saved_path: str | Path | None = None
        if auto_save:
            saved_path = save_text_output(effective_mode, project, effective_language, enriched_topic, result, engine_status)
            st.session_state.naz_text_saved_path = str(saved_path)

        pipeline_result = persist_generated_text(
            mode=effective_mode,
            project=project,
            language=effective_language,
            topic=enriched_topic,
            model=model,
            engine_status=engine_status,
            result=result,
            saved_path=saved_path,
            auto_image_job_for_prompt_improver=True,
            extra={"selected_mode": mode, "style": style, "length": length, "template_first": template_first, "auto_save": auto_save},
        )
        st.session_state.naz_text_last_metadata_path = pipeline_result.get("metadata_path", "")
        if pipeline_result.get("image_job_path"):
            st.session_state.naz_text_last_job_path = pipeline_result["image_job_path"]

        status_parts = ["Generated and displayed.", f"Metadata saved: {st.session_state.naz_text_last_metadata_path}"]
        if saved_path:
            status_parts.append(f"Auto-saved for workflow: {saved_path}")
        else:
            status_parts.append("Not text auto-saved; press Save current output only if needed.")
        if st.session_state.naz_text_last_job_path:
            status_parts.append(f"Auto image job created: {st.session_state.naz_text_last_job_path}")
        st.session_state.naz_text_pending_success = "\n".join(status_parts)
        if warnings:
            st.session_state.naz_text_pending_warning = "\n".join(warnings)
        st.rerun()

    render_pending_messages()
    output_text = st.text_area("Output", height=360, key=output_area_key())
    st.session_state.naz_text_output = output_text

    if st.session_state.naz_text_engine_status:
        st.caption(f"Engine status: {st.session_state.naz_text_engine_status}")
    if st.session_state.naz_text_saved_path:
        st.success(f"Last saved: {st.session_state.naz_text_saved_path}")
    if st.session_state.naz_text_last_metadata_path:
        st.info(f"Last metadata: {st.session_state.naz_text_last_metadata_path}")
    if st.session_state.naz_text_last_job_path:
        st.info(f"Last image job: {st.session_state.naz_text_last_job_path}")

    save_mode = st.session_state.naz_text_last_mode or internal_mode
    save_project = st.session_state.naz_text_last_project or project
    save_language = st.session_state.naz_text_last_language or language
    save_topic = st.session_state.naz_text_last_topic or enriched_topic
    save_model = st.session_state.naz_text_last_model or model
    current_output = get_current_output()

    if save:
        if not current_output.strip():
            st.error("No output to save.")
        else:
            saved_path = save_text_output(save_mode, save_project, save_language, save_topic, current_output, st.session_state.naz_text_engine_status or "manual_save")
            st.session_state.naz_text_saved_path = str(saved_path)
            pipeline_result = persist_generated_text(
                mode=save_mode,
                project=save_project,
                language=save_language,
                topic=save_topic,
                model=save_model,
                engine_status=st.session_state.naz_text_engine_status or "manual_save",
                result=current_output,
                saved_path=saved_path,
                auto_image_job_for_prompt_improver=False,
                extra={"manual_save": True},
            )
            st.session_state.naz_text_last_metadata_path = pipeline_result.get("metadata_path", "")
            st.success(f"Saved: {saved_path}")
            st.info(f"Metadata saved: {st.session_state.naz_text_last_metadata_path}")

    if send_image:
        if not current_output.strip():
            st.error("No output to send.")
        else:
            source = Path(st.session_state.naz_text_saved_path) if st.session_state.naz_text_saved_path else None
            image_prompt = current_output if save_mode == "Prompt Improver" else template_prompt(save_topic + "\n" + current_output[:500])
            job_path = create_image_job_from_text(
                project=save_project,
                mode=save_mode,
                topic=save_topic,
                output_text=image_prompt,
                source_text_path=source,
                metadata_path=st.session_state.naz_text_last_metadata_path,
                auto_export=False,
            )
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
    selected = render_nav(["Chat outputs", "Text outputs", "Scripts", "Image prompts", "Image jobs", "Text metadata"], key="text_library_sub", variant="sub")
    mapping = {
        "Chat outputs": (CHAT_OUTPUTS, TEXT_EXTENSIONS),
        "Text outputs": (TEXT_OUTPUTS, TEXT_EXTENSIONS),
        "Scripts": (SCRIPT_OUTPUTS, TEXT_EXTENSIONS),
        "Image prompts": (IMAGE_PROMPTS, TEXT_EXTENSIONS),
        "Image jobs": (IMAGE_JOBS, JSON_EXTENSIONS),
        "Text metadata": (TEXT_METADATA, JSON_EXTENSIONS),
    }
    folder, ext = mapping[selected]
    render_library_section(folder, ext, selected)


def render_status() -> None:
    st.markdown("### Backend Status")
    model = st.selectbox("Check model", AVAILABLE_MODELS, index=0, key="naz_text_check_model")
    names = installed_model_names()
    persistence_status = ensure_ollama_persistence()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Phase", "Text backend ready")
    c2.metric("Selected model installed", "yes" if model_installed(model) else "no")
    c3.metric("Installed models", len(names))
    c4.metric("Ollama persistence", "ok" if persistence_status.get("ok") else "check")
    st.json({
        "recommended_text_model": RECOMMENDED_TEXT_MODEL,
        "minimum_cpu_text_model": MINIMUM_CPU_TEXT_MODEL,
        "allowed_text_models": AVAILABLE_MODELS,
        "blocked_text_models": BLOCKED_TEXT_MODELS,
        "selected_model": model,
        "installed_models": names,
        "chat_outputs": str(CHAT_OUTPUTS),
        "text_outputs": str(TEXT_OUTPUTS),
        "script_outputs": str(SCRIPT_OUTPUTS),
        "image_prompts": str(IMAGE_PROMPTS),
        "image_jobs": str(IMAGE_JOBS),
        "text_metadata": str(TEXT_METADATA),
        "bangla_safe_mode": "available/default on",
        "model_policy": model_policy_status(),
        "mode_policy": MODE_POLICY,
        "backend_modes": list(MODE_CONFIG.keys()),
        "casual_chat_detection": "enabled",
        "prompt_improver_auto_image_job": "enabled",
        "manual_image_job_schema": "1.20",
        "ollama_persistence": persistence_status,
    })


def render_text_panel() -> None:
    st.subheader("Text Workstation")
    st.write("Generate scripts, stories, captions, free writing, chat replies, and image prompts directly from Naz Lab. Save outputs, metadata, and image queue jobs from one place.")
    col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
    col_a.metric("Chat outputs", count_files(CHAT_OUTPUTS))
    col_b.metric("Text outputs", count_files(TEXT_OUTPUTS))
    col_c.metric("Script outputs", count_files(SCRIPT_OUTPUTS))
    col_d.metric("Image prompts", count_files(IMAGE_PROMPTS))
    col_e.metric("Image jobs", count_files(IMAGE_JOBS))
    col_f.metric("Text metadata", count_files(TEXT_METADATA))
    selected = render_nav(["Create", "Library", "Backend Status"], key="text_sub", variant="sub")
    if selected == "Create":
        render_builder()
    elif selected == "Library":
        render_library()
    elif selected == "Backend Status":
        render_status()
