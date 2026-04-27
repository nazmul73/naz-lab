"""Naz Lab Phase 1.3 Text Workstation.

A lightweight Streamlit workstation for general chat and flexible text-generation modes.
It uses Ollama as the local LLM backend and writes outputs, logs, status, and
image job queue items to Google Drive via the Phase 0 shared utilities.
"""

from __future__ import annotations

import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests
import streamlit as st

# Allow running from /content/naz-lab/text_workstation/app.py in Colab.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    CHAT_OUTPUTS,
    IMAGE_JOBS,
    IMAGE_PROMPTS,
    OUTPUT_LOG_JSON,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import (  # noqa: E402
    append_output_log,
    safe_write_json,
    update_workstation_status,
)

OLLAMA_GENERATE_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_HEALTH_ENDPOINT = "http://localhost:11434/api/tags"
DEFAULT_MODEL = "gemma2:2b"
CPU_FALLBACK_MODEL = "tinyllama"
OPTIONAL_MODEL = "mistral"
AVAILABLE_MODELS = [DEFAULT_MODEL, CPU_FALLBACK_MODEL, OPTIONAL_MODEL]

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

MODE_CONFIG = {
    "Free Writer": {"prompt_file": "free_writer.md", "output_dir": TEXT_OUTPUTS, "prefix": "free_writer"},
    "Re-writer": {"prompt_file": "rewriter.md", "output_dir": TEXT_OUTPUTS, "prefix": "rewriter"},
    "Story Writer": {"prompt_file": "story_writer.md", "output_dir": TEXT_OUTPUTS, "prefix": "story_writer"},
    "Viral Script Writer": {"prompt_file": "viral_script_writer.md", "output_dir": SCRIPT_OUTPUTS, "prefix": "viral_script_writer"},
    "Caption Writer": {"prompt_file": "caption_writer.md", "output_dir": TEXT_OUTPUTS, "prefix": "caption_writer"},
    "Prompt Improver": {"prompt_file": "prompt_improver.md", "output_dir": IMAGE_PROMPTS, "prefix": "prompt_improver"},
}

MODE_HELP = {
    "Free Writer": "Universal writing mode for posts, emails, letters, scripts, captions, summaries, translations, and content plans.",
    "Re-writer": "Rewrite, polish, simplify, expand, shorten, translate, or change tone while preserving meaning.",
    "Story Writer": "Turn any topic into a clear story format.",
    "Viral Script Writer": "Turn any topic into a short-form video script.",
    "Caption Writer": "Create captions for any topic or platform.",
    "Prompt Improver": "Improve image, video, thumbnail, scene, or visual prompt ideas. Also creates an Image Workstation job JSON.",
}


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def state_key(mode: str, suffix: str) -> str:
    normalized = mode.lower().replace(" ", "_").replace("-", "_")
    return f"{normalized}_{suffix}"


def ensure_phase_0_ready() -> list[str]:
    required = [
        BASE_PATH,
        CHAT_OUTPUTS,
        TEXT_OUTPUTS,
        SCRIPT_OUTPUTS,
        IMAGE_PROMPTS,
        IMAGE_JOBS,
        WORKSTATION_LINKS_JSON,
        OUTPUT_LOG_JSON,
    ]
    return [str(path) for path in required if not path.exists()]


def read_prompt(prompt_file: str) -> str:
    path = PROMPTS_DIR / prompt_file
    if not path.exists():
        return "You are a helpful Naz Lab assistant. Accept any topic from the user."
    return path.read_text(encoding="utf-8").strip()


def call_ollama(prompt: str, model: str, system_prompt: str | None = None, timeout: int = 300) -> str:
    final_prompt = prompt if not system_prompt else f"{system_prompt}\n\nUser:\n{prompt}"
    payload = {"model": model, "prompt": final_prompt, "stream": False}
    response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def get_ollama_tags() -> dict:
    response = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=15)
    response.raise_for_status()
    return response.json()


def installed_model_names(tags: dict) -> list[str]:
    models = tags.get("models", [])
    names: list[str] = []
    for item in models:
        name = item.get("name")
        if name:
            names.append(name)
    return names


def save_text_output(output_dir: Path, prefix: str, content: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{prefix}_{now_stamp()}.txt"
    path.write_text(content, encoding="utf-8")
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="text_workstation",
        event="output_saved",
        details={"path": str(path), "prefix": prefix},
    )
    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "text_workstation",
        {"status": "running", "last_output_path": str(path)},
    )
    return path


def create_image_job(prompt_text: str) -> Path:
    IMAGE_JOBS.mkdir(parents=True, exist_ok=True)
    job_id = str(uuid.uuid4())
    job_path = IMAGE_JOBS / f"image_job_{now_stamp()}_{job_id[:8]}.json"
    job_data = {
        "job_id": job_id,
        "source_workstation": "text_workstation",
        "source_mode": "Prompt Improver",
        "status": "pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "prompt": prompt_text,
        "notes": "Generated by Text Workstation Prompt Improver",
    }
    safe_write_json(job_path, job_data)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="text_workstation",
        event="image_job_created",
        details={"job_path": str(job_path), "job_id": job_id},
    )
    return job_path


def list_text_files(directories: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for directory in directories:
        if directory.exists():
            files.extend(directory.glob("*.txt"))
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def save_chat_transcript(messages: list[dict[str, str]]) -> Path:
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        lines.append(f"[{role}]\n{content}\n")
    return save_text_output(CHAT_OUTPUTS, "chat", "\n".join(lines))


def render_backend_badge(model: str) -> None:
    try:
        tags = get_ollama_tags()
        names = installed_model_names(tags)
        if any(name == model or name.startswith(f"{model}:") for name in names):
            st.success(f"Backend ready. Selected model found: {model}")
        else:
            st.warning(f"Ollama is running, but selected model is not listed: {model}")
            st.caption("Use the Colab launcher to pull the model, then refresh this app.")
    except Exception as exc:
        st.error(f"Ollama backend is not reachable: {exc}")
        st.caption("Restart the Colab launcher or check /content/ollama.log.")


def render_general_chat(model: str) -> None:
    st.subheader("General Chat")
    st.caption("Normal assistant mode. Ask about content, Colab, coding, business, prompts, planning, and general knowledge.")
    system_prompt = read_prompt("general_chat.md")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()
    with col_b:
        if st.button("Save Chat"):
            if st.session_state.chat_messages:
                path = save_chat_transcript(st.session_state.chat_messages)
                st.success(f"Chat saved: {path}")
            else:
                st.info("No chat messages to save yet.")

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Message Naz Lab General Assistant...")
    if user_prompt:
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        conversation = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_messages[-10:])
        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = call_ollama(conversation, model=model, system_prompt=system_prompt)
                    st.markdown(answer)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        except requests.exceptions.Timeout:
            st.error("Ollama request timed out. On CPU runtime, switch to tinyllama or use a shorter prompt.")
        except Exception as exc:
            st.error(f"Ollama connection error: {exc}")
            st.caption("Check that the Colab launcher cell is still running Ollama and Streamlit.")


def clear_mode_state(mode: str) -> None:
    for suffix in ["input", "output", "saved_path", "job_path", "status"]:
        key = state_key(mode, suffix)
        if key in st.session_state:
            del st.session_state[key]


def render_writer_mode(mode: str, model: str) -> None:
    config = MODE_CONFIG[mode]
    st.subheader(mode)
    st.caption(MODE_HELP.get(mode, "Accept any topic. The mode controls format, not topic."))

    input_key = state_key(mode, "input")
    output_key = state_key(mode, "output")
    saved_path_key = state_key(mode, "saved_path")
    job_path_key = state_key(mode, "job_path")
    status_key = state_key(mode, "status")

    st.session_state.setdefault(input_key, "")
    st.session_state.setdefault(output_key, "")
    st.session_state.setdefault(saved_path_key, "")
    st.session_state.setdefault(job_path_key, "")
    st.session_state.setdefault(status_key, "Ready")

    system_prompt = read_prompt(config["prompt_file"])

    with st.form(key=f"{state_key(mode, 'form')}"):
        user_input = st.text_area(
            "Input context or topic",
            value=st.session_state[input_key],
            height=210,
            placeholder="Write any topic or task here. The selected mode controls the output format.",
        )
        col_a, col_b = st.columns(2)
        with col_a:
            generate_clicked = st.form_submit_button(f"Generate {mode}", use_container_width=True)
        with col_b:
            save_input_clicked = st.form_submit_button("Save Input Only", use_container_width=True)

    if save_input_clicked:
        st.session_state[input_key] = user_input
        st.session_state[status_key] = "Input saved in session state."
        st.success("Input saved. You can switch tabs/modes and come back.")

    if generate_clicked:
        st.session_state[input_key] = user_input
        if not user_input.strip():
            st.warning("Please provide input first.")
            return
        try:
            st.session_state[status_key] = "Generating..."
            with st.spinner("Generating... This can take longer on CPU runtime."):
                result = call_ollama(user_input, model=model, system_prompt=system_prompt)
            if not result:
                st.session_state[status_key] = "No text returned from Ollama. Try a shorter prompt or restart Ollama."
                st.warning(st.session_state[status_key])
                return
            st.session_state[output_key] = result
            path = save_text_output(config["output_dir"], config["prefix"], result)
            st.session_state[saved_path_key] = str(path)
            st.session_state[status_key] = "Done"
            if mode == "Prompt Improver":
                job_path = create_image_job(result)
                st.session_state[job_path_key] = str(job_path)
        except requests.exceptions.Timeout:
            st.session_state[status_key] = "Timed out. On CPU runtime this model may be too slow. Use tinyllama or switch to T4 GPU."
            st.error(st.session_state[status_key])
            return
        except requests.exceptions.ConnectionError:
            st.session_state[status_key] = "Cannot connect to Ollama. Restart the Colab launcher cell and confirm Ollama is running."
            st.error(st.session_state[status_key])
            return
        except Exception as exc:
            st.session_state[status_key] = f"Ollama connection error: {exc}"
            st.error(st.session_state[status_key])
            return

    col_clear, col_status = st.columns([1, 3])
    with col_clear:
        if st.button("Clear This Mode", key=f"clear_{state_key(mode, 'button')}"):
            clear_mode_state(mode)
            st.rerun()
    with col_status:
        st.caption(f"Status: {st.session_state.get(status_key, 'Ready')}")

    if st.session_state.get(input_key):
        with st.expander("Current saved input", expanded=False):
            st.write(st.session_state[input_key])

    if st.session_state.get(output_key):
        st.markdown("### Output")
        st.write(st.session_state[output_key])
        if st.session_state.get(saved_path_key):
            st.success(f"Saved: {st.session_state[saved_path_key]}")
        if mode == "Prompt Improver" and st.session_state.get(job_path_key):
            st.success(f"Image job created: {st.session_state[job_path_key]}")


def render_output_library() -> None:
    st.subheader("Output Library")
    files = list_text_files([CHAT_OUTPUTS, TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS])
    if not files:
        st.info("No saved outputs yet.")
        return

    display = [str(path) for path in files[:80]]
    selected = st.selectbox("Select output file", display)
    if selected:
        path = Path(selected)
        st.caption(str(path))
        st.text_area("Preview", path.read_text(encoding="utf-8"), height=320)


def render_settings(model: str) -> None:
    st.subheader("Settings")
    st.caption("Use this page to verify the Ollama backend, test the selected model, and save the current Cloudflare URL.")

    render_backend_badge(model)

    st.markdown("### Public URL")
    public_url = st.text_input("Public Cloudflare URL", value="")
    if st.button("Save Public URL"):
        update_workstation_status(
            WORKSTATION_LINKS_JSON,
            "text_workstation",
            {"public_url": public_url, "last_url_updated": datetime.now().isoformat(timespec="seconds")},
        )
        st.success("Public URL saved to workstation_links.json")

    st.markdown("### Backend checks")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Check Ollama Health", use_container_width=True):
            try:
                tags = get_ollama_tags()
                st.json(tags)
            except Exception as exc:
                st.error(f"Ollama health check failed: {exc}")
    with col_b:
        if st.button("Test Selected Model", use_container_width=True):
            try:
                start = time.time()
                answer = call_ollama("Reply with only one word: OK", model=model, timeout=180)
                elapsed = round(time.time() - start, 2)
                st.success(f"Model replied in {elapsed}s")
                st.code(answer or "[empty response]")
            except requests.exceptions.Timeout:
                st.error("Selected model test timed out. Use tinyllama on CPU or switch Colab runtime to T4 GPU.")
            except Exception as exc:
                st.error(f"Selected model test failed: {exc}")

    st.markdown("### Recommended model")
    st.write(
        {
            "CPU runtime": CPU_FALLBACK_MODEL,
            "T4/GPU runtime": DEFAULT_MODEL,
            "optional_heavier_model": OPTIONAL_MODEL,
            "selected_model": model,
        }
    )

    st.markdown("### Paths")
    st.write(
        {
            "available_models": AVAILABLE_MODELS,
            "generate_endpoint": OLLAMA_GENERATE_ENDPOINT,
            "health_endpoint": OLLAMA_HEALTH_ENDPOINT,
            "base_path": str(BASE_PATH),
            "chat_outputs": str(CHAT_OUTPUTS),
            "text_outputs": str(TEXT_OUTPUTS),
            "script_outputs": str(SCRIPT_OUTPUTS),
            "image_prompts": str(IMAGE_PROMPTS),
            "image_jobs": str(IMAGE_JOBS),
            "workstation_links_json": str(WORKSTATION_LINKS_JSON),
            "output_log_json": str(OUTPUT_LOG_JSON),
        }
    )


def main() -> None:
    st.set_page_config(page_title="Naz Lab Text Workstation", page_icon="✍️", layout="wide")
    st.title("✍️ Naz Lab Text Workstation")
    st.caption("Phase 1.3: 2-cell launcher support, form-based writer UI, stable session persistence, and model testing.")

    missing = ensure_phase_0_ready()
    if missing:
        st.error("Phase 0 foundation appears incomplete. Run master_setup/init_drive_structure.py first.")
        st.code("\n".join(missing))
        return

    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": "running"})

    with st.sidebar:
        st.header("Naz Lab Core")
        model = st.selectbox("Model", AVAILABLE_MODELS, index=0, key="selected_model")
        page = st.radio(
            "Mode",
            [
                "General Chat",
                "Free Writer",
                "Re-writer",
                "Story Writer",
                "Viral Script Writer",
                "Caption Writer",
                "Prompt Improver",
                "Output Library",
                "Settings",
            ],
            key="selected_page",
        )
        if model == CPU_FALLBACK_MODEL:
            st.info("CPU fallback selected. Faster on CPU, lower quality than gemma2:2b.")
        elif model == DEFAULT_MODEL:
            st.info("Best default for T4/GPU runtime.")
        st.caption("Cloudflare Tunnel is primary. Localtunnel is fallback only.")

    if page == "General Chat":
        render_general_chat(model)
    elif page in MODE_CONFIG:
        render_writer_mode(page, model)
    elif page == "Output Library":
        render_output_library()
    elif page == "Settings":
        render_settings(model)


if __name__ == "__main__":
    main()
