"""Naz Lab Phase 1.6 Text Workstation.

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
CPU_FALLBACK_MODEL = "qwen2.5:0.5b"
LEGACY_MODEL = "tinyllama"
OPTIONAL_MODEL = "mistral"
AVAILABLE_MODELS = [CPU_FALLBACK_MODEL, DEFAULT_MODEL, LEGACY_MODEL, OPTIONAL_MODEL]

DEFAULT_NUM_PREDICT = 260
CPU_NUM_PREDICT = 180
TEST_NUM_PREDICT = 40
REQUEST_TIMEOUT_SECONDS = 180

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
    "Free Writer": "Universal writing mode for posts, emails, letters, scripts, captions, summaries, and content plans.",
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
    required = [BASE_PATH, CHAT_OUTPUTS, TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS, IMAGE_JOBS, WORKSTATION_LINKS_JSON, OUTPUT_LOG_JSON]
    return [str(path) for path in required if not path.exists()]


def read_prompt(prompt_file: str) -> str:
    path = PROMPTS_DIR / prompt_file
    if not path.exists():
        return "Answer the user's request directly. Keep the answer concise."
    return path.read_text(encoding="utf-8").strip()


def model_num_predict(model: str, requested: int | None = None) -> int:
    if requested is not None:
        return requested
    if model == CPU_FALLBACK_MODEL or model == LEGACY_MODEL:
        return CPU_NUM_PREDICT
    return DEFAULT_NUM_PREDICT


def build_prompt(user_prompt: str, system_prompt: str | None = None) -> str:
    if not system_prompt:
        return f"<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    return (
        "<|im_start|>system\n"
        f"{system_prompt}\n"
        "Important: Do not repeat these instructions. Write only the final answer."
        "<|im_end|>\n"
        "<|im_start|>user\n"
        f"{user_prompt}"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def clean_model_output(text: str) -> str:
    cleaned = text.strip()
    for token in ["<|im_end|>", "<|im_start|>"]:
        cleaned = cleaned.replace(token, "")
    leak_phrases = [
        "You are Naz Lab",
        "Your job:",
        "Rules:",
        "Important: Do not repeat",
        "Write only the final answer",
    ]
    if any(phrase in cleaned[:300] for phrase in leak_phrases):
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        filtered = [line for line in lines if not any(phrase in line for phrase in leak_phrases)]
        cleaned = "\n".join(filtered).strip()
    return cleaned.strip()


def call_ollama(prompt: str, model: str, system_prompt: str | None = None, timeout: int = REQUEST_TIMEOUT_SECONDS, num_predict: int | None = None) -> str:
    payload = {
        "model": model,
        "prompt": build_prompt(prompt, system_prompt),
        "stream": False,
        "options": {
            "num_predict": model_num_predict(model, num_predict),
            "temperature": 0.3,
            "top_p": 0.85,
            "repeat_penalty": 1.15,
            "stop": ["<|im_end|>", "<|im_start|>user", "USER:", "INSTRUCTION:", "TASK:"],
        },
    }
    response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return clean_model_output(data.get("response", ""))


def get_ollama_tags() -> dict:
    response = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=15)
    response.raise_for_status()
    return response.json()


def installed_model_names(tags: dict) -> list[str]:
    names: list[str] = []
    for item in tags.get("models", []):
        name = item.get("name")
        if name:
            names.append(name)
    return names


def save_text_output(output_dir: Path, prefix: str, content: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{prefix}_{now_stamp()}.txt"
    path.write_text(content, encoding="utf-8")
    append_output_log(OUTPUT_LOG_JSON, workstation="text_workstation", event="output_saved", details={"path": str(path), "prefix": prefix})
    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": "running", "last_output_path": str(path)})
    return path


def create_image_job(prompt_text: str) -> Path:
    IMAGE_JOBS.mkdir(parents=True, exist_ok=True)
    job_id = str(uuid.uuid4())
    job_path = IMAGE_JOBS / f"image_job_{now_stamp()}_{job_id[:8]}.json"
    safe_write_json(job_path, {"job_id": job_id, "source_workstation": "text_workstation", "source_mode": "Prompt Improver", "status": "pending", "created_at": datetime.now().isoformat(timespec="seconds"), "prompt": prompt_text, "notes": "Generated by Text Workstation Prompt Improver"})
    append_output_log(OUTPUT_LOG_JSON, workstation="text_workstation", event="image_job_created", details={"job_path": str(job_path), "job_id": job_id})
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
        lines.append(f"[{msg.get('role', 'unknown')}]\n{msg.get('content', '')}\n")
    return save_text_output(CHAT_OUTPUTS, "chat", "\n".join(lines))


def render_backend_badge(model: str) -> None:
    try:
        tags = get_ollama_tags()
        names = installed_model_names(tags)
        if any(name == model or name.startswith(f"{model}:") for name in names):
            st.success(f"Backend ready. Selected model found: {model}")
        else:
            st.warning(f"Ollama is running, but selected model is not listed: {model}")
            st.caption("Run Cell 2 launcher again to pull the recommended model.")
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
                st.success(f"Chat saved: {save_chat_transcript(st.session_state.chat_messages)}")
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
            st.error("Ollama request timed out. Use qwen2.5:0.5b on CPU or switch to T4 GPU.")
        except Exception as exc:
            st.error(f"Ollama connection error: {exc}")


def clear_mode_state(mode: str) -> None:
    for suffix in ["input", "output", "saved_path", "job_path", "status", "elapsed"]:
        st.session_state.pop(state_key(mode, suffix), None)


def render_writer_mode(mode: str, model: str) -> None:
    config = MODE_CONFIG[mode]
    st.subheader(mode)
    st.caption(MODE_HELP.get(mode, "Accept any topic. The mode controls format, not topic."))
    input_key = state_key(mode, "input")
    output_key = state_key(mode, "output")
    saved_path_key = state_key(mode, "saved_path")
    job_path_key = state_key(mode, "job_path")
    status_key = state_key(mode, "status")
    elapsed_key = state_key(mode, "elapsed")
    for key, default in [(input_key, ""), (output_key, ""), (saved_path_key, ""), (job_path_key, ""), (status_key, "Ready"), (elapsed_key, "")]:
        st.session_state.setdefault(key, default)
    system_prompt = read_prompt(config["prompt_file"])
    with st.form(key=f"{state_key(mode, 'form')}"):
        user_input = st.text_area("Input context or topic", value=st.session_state[input_key], height=210, placeholder="Write any topic or task here. The selected mode controls the output format.")
        col_a, col_b = st.columns(2)
        with col_a:
            generate_clicked = st.form_submit_button(f"Generate {mode}", use_container_width=True)
        with col_b:
            quick_clicked = st.form_submit_button("Quick Test", use_container_width=True)
    if generate_clicked or quick_clicked:
        st.session_state[input_key] = user_input
        if not user_input.strip():
            st.warning("Please provide input first.")
            return
        try:
            st.session_state[status_key] = "Generating..."
            start = time.time()
            limit = TEST_NUM_PREDICT if quick_clicked else model_num_predict(model)
            with st.spinner(f"Generating with {model}. Token limit: {limit}"):
                result = call_ollama(user_input, model=model, system_prompt=system_prompt, num_predict=limit)
            st.session_state[elapsed_key] = f"{round(time.time() - start, 2)}s"
            if not result:
                st.session_state[status_key] = "No text returned from Ollama. Try qwen2.5:0.5b or restart Ollama."
                st.warning(st.session_state[status_key])
                return
            st.session_state[output_key] = result
            st.session_state[saved_path_key] = str(save_text_output(config["output_dir"], config["prefix"], result))
            st.session_state[status_key] = "Done"
            if mode == "Prompt Improver":
                st.session_state[job_path_key] = str(create_image_job(result))
            st.rerun()
        except requests.exceptions.Timeout:
            st.session_state[status_key] = "Timed out. Use qwen2.5:0.5b on CPU or switch to T4 GPU."
            st.error(st.session_state[status_key])
            return
        except requests.exceptions.ConnectionError:
            st.session_state[status_key] = "Cannot connect to Ollama. Restart Cell 2 launcher and refresh the Cloudflare page."
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
        elapsed = st.session_state.get(elapsed_key, "")
        suffix = f" | Last generation: {elapsed}" if elapsed else ""
        st.caption(f"Status: {st.session_state.get(status_key, 'Ready')}{suffix}")
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
    selected = st.selectbox("Select output file", [str(path) for path in files[:80]])
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
        update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"public_url": public_url, "last_url_updated": datetime.now().isoformat(timespec="seconds")})
        st.success("Public URL saved to workstation_links.json")
    st.markdown("### Backend checks")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Check Ollama Health", use_container_width=True):
            try:
                st.json(get_ollama_tags())
            except Exception as exc:
                st.error(f"Ollama health check failed: {exc}")
    with col_b:
        if st.button("Test Selected Model", use_container_width=True):
            try:
                start = time.time()
                answer = call_ollama("Write one short sentence: AI saves time.", model=model, timeout=120, num_predict=TEST_NUM_PREDICT)
                st.success(f"Model replied in {round(time.time() - start, 2)}s")
                st.code(answer or "[empty response]")
            except requests.exceptions.Timeout:
                st.error("Selected model test timed out. Use qwen2.5:0.5b on CPU or switch Colab runtime to T4 GPU.")
            except Exception as exc:
                st.error(f"Selected model test failed: {exc}")
    st.markdown("### Recommended model")
    st.write({"CPU runtime": CPU_FALLBACK_MODEL, "T4/GPU runtime": DEFAULT_MODEL, "legacy_not_recommended": LEGACY_MODEL, "optional_heavier_model": OPTIONAL_MODEL, "selected_model": model, "cpu_token_limit": CPU_NUM_PREDICT, "default_token_limit": DEFAULT_NUM_PREDICT, "quick_test_token_limit": TEST_NUM_PREDICT})
    st.markdown("### Paths")
    st.write({"available_models": AVAILABLE_MODELS, "generate_endpoint": OLLAMA_GENERATE_ENDPOINT, "health_endpoint": OLLAMA_HEALTH_ENDPOINT, "base_path": str(BASE_PATH), "chat_outputs": str(CHAT_OUTPUTS), "text_outputs": str(TEXT_OUTPUTS), "script_outputs": str(SCRIPT_OUTPUTS), "image_prompts": str(IMAGE_PROMPTS), "image_jobs": str(IMAGE_JOBS), "workstation_links_json": str(WORKSTATION_LINKS_JSON), "output_log_json": str(OUTPUT_LOG_JSON)})


def render_direct_test(model: str) -> None:
    st.subheader("Direct Test")
    st.caption("Use this to isolate Ollama/model response without writer prompt files.")
    prompt = st.text_input("Test prompt", value="Write one short sentence: AI saves time.")
    if st.button("Run Direct Test"):
        try:
            start = time.time()
            answer = call_ollama(prompt, model=model, system_prompt=None, timeout=120, num_predict=TEST_NUM_PREDICT)
            st.success(f"Direct test completed in {round(time.time() - start, 2)}s")
            st.code(answer or "[empty response]")
        except Exception as exc:
            st.error(f"Direct test failed: {exc}")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Text Workstation", page_icon="✍️", layout="wide")
    st.title("✍️ Naz Lab Text Workstation")
    st.caption("Phase 1.6: qwen2.5:0.5b CPU fallback, TinyLlama marked legacy, cleaner instruction following.")
    missing = ensure_phase_0_ready()
    if missing:
        st.error("Phase 0 foundation appears incomplete. Run master_setup/init_drive_structure.py first.")
        st.code("\n".join(missing))
        return
    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": "running"})
    with st.sidebar:
        st.header("Naz Lab Core")
        model = st.selectbox("Model", AVAILABLE_MODELS, index=0, key="selected_model")
        page = st.radio("Mode", ["General Chat", "Free Writer", "Re-writer", "Story Writer", "Viral Script Writer", "Caption Writer", "Prompt Improver", "Output Library", "Settings", "Direct Test"], key="selected_page")
        if model == CPU_FALLBACK_MODEL:
            st.info("Recommended CPU fallback selected.")
        elif model == LEGACY_MODEL:
            st.warning("tinyllama is legacy and not recommended for writing quality.")
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
    elif page == "Direct Test":
        render_direct_test(model)


if __name__ == "__main__":
    main()
