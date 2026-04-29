"""Naz Lab AI Workstation root Streamlit app.

This app.py is intentionally self-contained while still following the Naz Lab
Drive directory convention. It fixes three production issues:

1. Ollama persistence: use a Drive-backed model store for gemma2:2b.
2. Prompt Improver queue: save refined prompts as JSON jobs in NazLab/image_jobs.
3. Streaming UX: render Ollama output progressively in Streamlit.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import requests
import streamlit as st

# -----------------------------------------------------------------------------
# Naz Lab paths
# -----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BASE_DIR = Path("/content/drive/MyDrive/NazLab")
OUTPUT_DIR = BASE_DIR / "outputs"
TEXT_OUTPUT_DIR = BASE_DIR / "text_outputs"
CHAT_OUTPUT_DIR = BASE_DIR / "chat_outputs"
SCRIPT_OUTPUT_DIR = BASE_DIR / "script_outputs"
IMAGE_PROMPTS_DIR = BASE_DIR / "image_prompts"
IMAGE_JOB_DIR = BASE_DIR / "image_jobs"
VOICE_JOB_DIR = BASE_DIR / "voice_jobs"
VIDEO_JOB_DIR = BASE_DIR / "video_jobs"
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
DRIVE_OLLAMA_MODELS_DIR = MODELS_DIR / "ollama"
LOCAL_OLLAMA_MODELS_DIR = Path.home() / ".ollama" / "models"

CUSTOM_GEMS_PATH = CONFIG_DIR / "custom_gems.json"
TOOL_LINKS_PATH = CONFIG_DIR / "tool_links.json"
APP_LOG_PATH = LOGS_DIR / "app_log.jsonl"

REQUIRED_DIRS = [
    BASE_DIR,
    OUTPUT_DIR,
    TEXT_OUTPUT_DIR,
    CHAT_OUTPUT_DIR,
    SCRIPT_OUTPUT_DIR,
    IMAGE_PROMPTS_DIR,
    IMAGE_JOB_DIR,
    VOICE_JOB_DIR,
    VIDEO_JOB_DIR,
    CONFIG_DIR,
    LOGS_DIR,
    MODELS_DIR,
    DRIVE_OLLAMA_MODELS_DIR,
]

# -----------------------------------------------------------------------------
# Ollama config
# -----------------------------------------------------------------------------

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_HOST}/api/generate"
OLLAMA_HEALTH_ENDPOINT = f"{OLLAMA_HOST}/api/tags"
DEFAULT_MODEL = "gemma2:2b"
FALLBACK_MODEL = "qwen2.5:1.5b"
AVAILABLE_MODELS = [DEFAULT_MODEL, FALLBACK_MODEL]
REQUEST_TIMEOUT_SECONDS = 300

MODE_CONFIG: dict[str, dict[str, Any]] = {
    "General Chat": {"output_dir": CHAT_OUTPUT_DIR, "prefix": "general_chat", "save_default": False},
    "Free Writer": {"output_dir": TEXT_OUTPUT_DIR, "prefix": "free_writer", "save_default": False},
    "Story Writer": {"output_dir": TEXT_OUTPUT_DIR, "prefix": "story_writer", "save_default": True},
    "Viral Script Writer": {"output_dir": SCRIPT_OUTPUT_DIR, "prefix": "viral_script_writer", "save_default": True},
    "Caption Writer": {"output_dir": TEXT_OUTPUT_DIR, "prefix": "caption_writer", "save_default": False},
    "Prompt Improver": {"output_dir": IMAGE_PROMPTS_DIR, "prefix": "prompt_improver", "save_default": True},
}

LENGTH_TOKEN_LIMITS = {"Short": 220, "Medium": 420, "Long": 700}

GENERAL_CHAT_SYSTEM_PROMPT = """You are Naz Lab General Assistant.
Answer naturally in the user's language. Help with content creation, coding,
Colab errors, business, productivity, prompts, and planning. Be direct,
practical, and avoid unnecessary formatting unless useful."""

MODE_INSTRUCTIONS = {
    "General Chat": "Reply conversationally and directly.",
    "Free Writer": "Write a complete ready-to-use draft.",
    "Story Writer": "Use sections: Title, Setup, Main Event, Turning Point, Ending, Question CTA.",
    "Viral Script Writer": "Use sections: Title, Hook, Voiceover, On-screen text, Caption, CTA.",
    "Caption Writer": "Write three practical caption options.",
    "Prompt Improver": "Rewrite the user's idea as one polished visual image prompt. Include subject, setting, mood, lighting, camera/style, and practical constraints. Return only the refined prompt.",
}

# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(text: str, max_len: int = 80) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text)).strip("_")
    return slug[:max_len] or "naz_lab"


def append_log(event: str, details: dict[str, Any]) -> None:
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": now_iso(), "event": event, "details": details}
        with APP_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        write_json(path, default)
        return default
    try:
        raw = path.read_text(encoding="utf-8").strip()
        return json.loads(raw) if raw else default
    except Exception:
        backup = path.with_name(f"{path.stem}_corrupted_{now_stamp()}{path.suffix}")
        try:
            path.rename(backup)
        except Exception:
            pass
        write_json(path, default)
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_directories() -> None:
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Drive + Ollama persistence
# -----------------------------------------------------------------------------


def mount_drive_if_colab() -> dict[str, Any]:
    status = {"ok": False, "running_in_colab": False, "message": "Drive mount not attempted."}
    try:
        from google.colab import drive  # type: ignore

        status["running_in_colab"] = True
        drive.mount("/content/drive", force_remount=False)
        status.update({"ok": BASE_DIR.parent.exists(), "message": "Google Drive mounted."})
        if not BASE_DIR.parent.exists():
            status["message"] = f"Drive mount returned, but {BASE_DIR.parent} is not visible."
    except ModuleNotFoundError:
        status.update({"ok": True, "running_in_colab": False, "message": "Not running in Colab; Drive mount skipped."})
    except Exception as exc:
        status.update({"ok": False, "message": f"Drive mount failed: {type(exc).__name__}: {exc}"})
    return status


def path_has_model_store(path: Path) -> bool:
    if not path.exists():
        return False
    manifests = path / "manifests"
    blobs = path / "blobs"
    return manifests.exists() and blobs.exists() and any(path.rglob("*"))


def copy_local_models_to_drive(local_dir: Path, drive_dir: Path) -> int:
    copied = 0
    if not local_dir.exists() or local_dir.is_symlink():
        return copied
    drive_dir.mkdir(parents=True, exist_ok=True)
    for item in local_dir.iterdir():
        target = drive_dir / item.name
        if target.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
        copied += 1
    return copied


def ensure_ollama_persistence(required_model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Create a Drive-backed Ollama model symlink before app generation starts."""
    status: dict[str, Any] = {
        "ok": False,
        "required_model": required_model,
        "local_models_dir": str(LOCAL_OLLAMA_MODELS_DIR),
        "drive_models_dir": str(DRIVE_OLLAMA_MODELS_DIR),
        "mode": "not_started",
        "message": "",
    }
    try:
        DRIVE_OLLAMA_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        LOCAL_OLLAMA_MODELS_DIR.parent.mkdir(parents=True, exist_ok=True)
        os.environ["OLLAMA_MODELS"] = str(DRIVE_OLLAMA_MODELS_DIR)

        if LOCAL_OLLAMA_MODELS_DIR.is_symlink():
            status.update({"ok": True, "mode": "already_symlinked", "message": f"Local models path symlinked to {LOCAL_OLLAMA_MODELS_DIR.resolve()}"})
            return status

        if path_has_model_store(LOCAL_OLLAMA_MODELS_DIR):
            copied = copy_local_models_to_drive(LOCAL_OLLAMA_MODELS_DIR, DRIVE_OLLAMA_MODELS_DIR)
            backup = LOCAL_OLLAMA_MODELS_DIR.parent / "models_local_backup"
            if not backup.exists():
                LOCAL_OLLAMA_MODELS_DIR.rename(backup)
                LOCAL_OLLAMA_MODELS_DIR.symlink_to(DRIVE_OLLAMA_MODELS_DIR, target_is_directory=True)
                status.update({"ok": True, "mode": "migrated_local_to_drive", "copied_items": copied, "backup_dir": str(backup), "message": "Local Ollama models migrated to Drive and symlinked."})
                return status
            status.update({"ok": True, "mode": "local_store_kept", "message": "Local model store exists and backup already exists; OLLAMA_MODELS points to Drive."})
            return status

        if LOCAL_OLLAMA_MODELS_DIR.exists() and not any(LOCAL_OLLAMA_MODELS_DIR.iterdir()):
            LOCAL_OLLAMA_MODELS_DIR.rmdir()

        if not LOCAL_OLLAMA_MODELS_DIR.exists():
            LOCAL_OLLAMA_MODELS_DIR.symlink_to(DRIVE_OLLAMA_MODELS_DIR, target_is_directory=True)

        status.update({"ok": True, "mode": "created_symlink", "message": "Created Drive-backed Ollama model symlink."})
        return status
    except Exception as exc:
        status.update({"ok": False, "mode": "error", "message": f"Ollama persistence failed: {type(exc).__name__}: {exc}"})
        return status


def run_command(command: list[str], timeout: int = 60) -> tuple[bool, str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, output.strip()
    except FileNotFoundError:
        return False, f"Command not found: {command[0]}"
    except subprocess.TimeoutExpired:
        return False, f"Command timed out: {' '.join(command)}"
    except Exception as exc:
        return False, f"Command failed: {type(exc).__name__}: {exc}"


def start_ollama_server() -> dict[str, Any]:
    status = {"ok": False, "started": False, "message": ""}
    try:
        requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=3).raise_for_status()
        status.update({"ok": True, "started": False, "message": "Ollama server already running."})
        return status
    except Exception:
        pass

    if shutil.which("ollama") is None:
        status.update({"ok": False, "message": "Ollama CLI not found. Install Ollama in the Colab launcher first."})
        return status

    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(24):
            time.sleep(0.5)
            try:
                requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=3).raise_for_status()
                status.update({"ok": True, "started": True, "message": "Ollama server started."})
                return status
            except Exception:
                continue
        status.update({"ok": False, "message": "Ollama server did not become ready within 12 seconds."})
        return status
    except Exception as exc:
        status.update({"ok": False, "message": f"Failed to start Ollama server: {type(exc).__name__}: {exc}"})
        return status


def installed_models() -> list[str]:
    try:
        response = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=10)
        response.raise_for_status()
        return [item.get("name", "") for item in response.json().get("models", []) if item.get("name")]
    except Exception:
        return []


def model_available(model: str) -> bool:
    return any(name == model or name.startswith(f"{model}:") for name in installed_models())


def ensure_required_model(model: str = DEFAULT_MODEL) -> dict[str, Any]:
    status = {"ok": False, "model": model, "message": ""}
    if model_available(model):
        status.update({"ok": True, "message": f"Model available: {model}"})
        return status
    if shutil.which("ollama") is None:
        status.update({"ok": False, "message": "Ollama CLI unavailable; cannot pull missing model."})
        return status
    ok, output = run_command(["ollama", "pull", model], timeout=900)
    status.update({"ok": ok, "message": output[-1500:] if output else (f"Pulled {model}" if ok else f"Could not pull {model}")})
    return status


def initialize_runtime_once() -> None:
    if st.session_state.get("runtime_initialized"):
        return
    drive_status = mount_drive_if_colab()
    ensure_directories()
    persistence_status = ensure_ollama_persistence(DEFAULT_MODEL)
    server_status = start_ollama_server()
    model_status = {"ok": False, "model": DEFAULT_MODEL, "message": "Model check skipped because Ollama server is not ready."}
    if server_status.get("ok"):
        model_status = ensure_required_model(DEFAULT_MODEL)
    st.session_state.startup_status = {
        "drive": drive_status,
        "directories": {"base_dir": str(BASE_DIR), "image_job_dir": str(IMAGE_JOB_DIR)},
        "ollama_persistence": persistence_status,
        "ollama_server": server_status,
        "model": model_status,
    }
    st.session_state.runtime_initialized = True


# -----------------------------------------------------------------------------
# Generation + queue helpers
# -----------------------------------------------------------------------------


def build_system_instruction(mode: str, language: str, length: str) -> str:
    language_rule = "Write in clear English." if language == "English" else "Write in natural, simple Bangla unless the user asks otherwise."
    return "\n".join([
        "You are Naz Lab Text Workstation.",
        language_rule,
        MODE_INSTRUCTIONS.get(mode, "Answer directly."),
        f"Length: {length}.",
        "Return final output only. Do not repeat instructions.",
    ])


def build_prompt(user_prompt: str, mode: str, language: str, length: str) -> str:
    if mode == "General Chat":
        system_instruction = GENERAL_CHAT_SYSTEM_PROMPT
    else:
        system_instruction = build_system_instruction(mode, language, length)
    return f"<|im_start|>system\n{system_instruction}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"


def clean_chunk(text: str) -> str:
    return text.replace("<|im_end|>", "").replace("<|im_start|>", "")


def stream_ollama_response(user_prompt: str, model: str, mode: str, language: str, length: str) -> Generator[str, None, None]:
    payload = {
        "model": model,
        "prompt": build_prompt(user_prompt, mode, language, length),
        "stream": True,
        "options": {
            "num_predict": LENGTH_TOKEN_LIMITS.get(length, 420),
            "temperature": 0.25,
            "top_p": 0.9,
            "repeat_penalty": 1.12,
            "stop": ["<|im_end|>", "<|im_start|>user", "INSTRUCTION:", "TASK:"],
        },
    }
    with requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT_SECONDS, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            chunk = clean_chunk(str(data.get("response", "")))
            if chunk:
                yield chunk
            if data.get("done"):
                break


def save_text_output(mode: str, original_prompt: str, output: str, model: str) -> Path:
    config = MODE_CONFIG[mode]
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{config['prefix']}_{safe_slug(original_prompt)}_{now_stamp()}.txt"
    content = (
        "NAZ LAB TEXT OUTPUT\n"
        + "=" * 40
        + f"\nMode: {mode}\nModel: {model}\nTimestamp: {now_iso()}\n\nORIGINAL PROMPT:\n{original_prompt}\n\nOUTPUT:\n{output}\n"
    )
    path.write_text(content, encoding="utf-8")
    append_log("text_output_saved", {"path": str(path), "mode": mode, "model": model})
    return path


def save_prompt_improver_json_job(original_prompt: str, refined_prompt: str) -> Path:
    IMAGE_JOB_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": now_iso(),
        "original_prompt": original_prompt,
        "refined_prompt": refined_prompt,
    }
    path = IMAGE_JOB_DIR / f"prompt_improver_job_{now_stamp()}_{uuid.uuid4().hex[:8]}.json"
    write_json(path, payload)
    append_log("prompt_improver_json_job_saved", {"path": str(path)})
    return path


def save_chat_transcript(messages: list[dict[str, str]], model: str) -> Path:
    CHAT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = CHAT_OUTPUT_DIR / f"general_chat_{now_stamp()}.txt"
    lines = ["NAZ LAB GENERAL CHAT", "=" * 40, f"Model: {model}", f"Timestamp: {now_iso()}", ""]
    for message in messages:
        lines.append(f"{message.get('role', 'user').upper()}:\n{message.get('content', '')}\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    append_log("chat_saved", {"path": str(path)})
    return path


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Naz Lab AI Workstation", page_icon="🧪", layout="wide")
initialize_runtime_once()

if "last_output" not in st.session_state:
    st.session_state.last_output = ""
if "last_saved_path" not in st.session_state:
    st.session_state.last_saved_path = ""
if "last_job_path" not in st.session_state:
    st.session_state.last_job_path = ""
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "আমি Naz Lab General Assistant. আপনি content, coding, Colab error, prompt, planning—যেকোনো বিষয়ে কথা বলতে পারেন।"}
    ]

st.title("🧪 Naz Lab AI Workstation")
st.caption("Drive-persistent Ollama + streaming generation + Prompt Improver JSON queue")

with st.sidebar:
    st.header("Naz Lab Control")
    model = st.selectbox("Model", AVAILABLE_MODELS, index=0)
    language = st.selectbox("Language", ["Bangla", "English", "Mixed Bangla-English"], index=0)
    length = st.radio("Length", list(LENGTH_TOKEN_LIMITS.keys()), index=1)
    with st.expander("Runtime status", expanded=False):
        st.json(st.session_state.get("startup_status", {}))
    if st.button("Re-check Ollama", use_container_width=True):
        st.session_state.runtime_initialized = False
        st.rerun()

startup = st.session_state.get("startup_status", {})
if not startup.get("drive", {}).get("ok"):
    st.warning(startup.get("drive", {}).get("message", "Drive may not be mounted."))
if not startup.get("ollama_server", {}).get("ok"):
    st.error(startup.get("ollama_server", {}).get("message", "Ollama server is not ready."))
if not startup.get("model", {}).get("ok"):
    st.warning(startup.get("model", {}).get("message", f"{DEFAULT_MODEL} is not available yet."))

tabs = st.tabs(["Chat", "Text Builder", "Prompt Jobs", "Output Library", "Settings"])

with tabs[0]:
    st.header("General Chat")
    col_clear, col_save = st.columns(2)
    with col_clear:
        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()
    with col_save:
        if st.button("Save Chat"):
            try:
                saved = save_chat_transcript(st.session_state.chat_messages, model)
                st.success(f"Saved chat: {saved}")
            except Exception as exc:
                st.error(f"Chat save failed: {exc}")

    for message in st.session_state.chat_messages:
        with st.chat_message(message.get("role", "assistant")):
            st.markdown(message.get("content", ""))

    user_message = st.chat_input("Message Naz Lab...")
    if user_message:
        st.session_state.chat_messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            chunks: list[str] = []
            try:
                conversation = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_messages[-10:])
                for chunk in stream_ollama_response(conversation, model, "General Chat", language, length):
                    chunks.append(chunk)
                    placeholder.markdown("".join(chunks) + "▌")
                assistant_reply = "".join(chunks).strip()
                placeholder.markdown(assistant_reply or "No response returned.")
                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_reply})
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Ollama. Check `ollama serve`.")
            except requests.exceptions.Timeout:
                st.error("Ollama timed out. Try Short length or restart Ollama.")
            except Exception as exc:
                st.error(f"Chat generation failed: {type(exc).__name__}: {exc}")

with tabs[1]:
    st.header("Text Builder")
    mode = st.selectbox("Mode", list(MODE_CONFIG.keys()), index=list(MODE_CONFIG.keys()).index("Prompt Improver"))
    prompt = st.text_area("Input prompt", height=210, placeholder="Write your topic, script idea, caption request, or image prompt idea here...")
    generate = st.button("Generate Streaming Response", type="primary", use_container_width=True)

    if generate:
        if not prompt.strip():
            st.error("Input prompt is required.")
        else:
            placeholder = st.empty()
            chunks: list[str] = []
            started = time.time()
            try:
                if not model_available(model):
                    st.warning(f"Selected model is not currently listed by Ollama: {model}. Trying generation anyway.")
                for chunk in stream_ollama_response(prompt, model, mode, language, length):
                    chunks.append(chunk)
                    placeholder.markdown("".join(chunks) + "▌")
                final_output = "".join(chunks).strip()
                placeholder.markdown(final_output or "No text returned from Ollama.")
                st.session_state.last_output = final_output
                st.session_state.last_saved_path = ""
                st.session_state.last_job_path = ""

                if final_output and MODE_CONFIG[mode].get("save_default"):
                    saved_path = save_text_output(mode, prompt, final_output, model)
                    st.session_state.last_saved_path = str(saved_path)
                    st.success(f"Output saved: {saved_path}")

                if mode == "Prompt Improver" and final_output:
                    job_path = save_prompt_improver_json_job(prompt, final_output)
                    st.session_state.last_job_path = str(job_path)
                    st.success(f"Prompt Improver JSON job saved: {job_path}")

                append_log("generation_finished", {"mode": mode, "model": model, "elapsed_seconds": round(time.time() - started, 2)})
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Ollama. Restart the launcher or check `ollama serve`.")
            except requests.exceptions.Timeout:
                st.error("Ollama request timed out. Try Short length or restart Ollama.")
            except Exception as exc:
                st.error(f"Generation failed: {type(exc).__name__}: {exc}")

    if st.session_state.last_output:
        st.subheader("Last Output")
        st.text_area("Generated text", value=st.session_state.last_output, height=320)
    if st.session_state.last_saved_path:
        st.info(f"Last saved text: {st.session_state.last_saved_path}")
    if st.session_state.last_job_path:
        st.info(f"Last Prompt Improver JSON job: {st.session_state.last_job_path}")

with tabs[2]:
    st.header("Prompt Jobs")
    st.code(str(IMAGE_JOB_DIR))
    jobs = sorted(IMAGE_JOB_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:30] if IMAGE_JOB_DIR.exists() else []
    if not jobs:
        st.info("No Prompt Improver JSON jobs yet.")
    else:
        selected = st.selectbox("Select job", [str(job) for job in jobs])
        st.json(read_json(Path(selected), {}))

with tabs[3]:
    st.header("Output Library")
    folders = {
        "Outputs": OUTPUT_DIR,
        "Text outputs": TEXT_OUTPUT_DIR,
        "Chat outputs": CHAT_OUTPUT_DIR,
        "Scripts": SCRIPT_OUTPUT_DIR,
        "Image prompts": IMAGE_PROMPTS_DIR,
    }
    folder_label = st.selectbox("Folder", list(folders.keys()))
    folder = folders[folder_label]
    files = sorted(folder.glob("*.txt"), key=lambda item: item.stat().st_mtime, reverse=True)[:30] if folder.exists() else []
    if not files:
        st.info(f"No text files found in {folder}")
    else:
        selected_file = st.selectbox("Select output", [str(file) for file in files])
        st.code(selected_file)
        st.text_area("Preview", Path(selected_file).read_text(encoding="utf-8", errors="ignore"), height=360)

with tabs[4]:
    st.header("Settings")
    st.json({
        "ollama_endpoint": OLLAMA_GENERATE_ENDPOINT,
        "ollama_health_endpoint": OLLAMA_HEALTH_ENDPOINT,
        "base_dir": str(BASE_DIR),
        "drive_ollama_models": str(DRIVE_OLLAMA_MODELS_DIR),
        "local_ollama_models": str(LOCAL_OLLAMA_MODELS_DIR),
        "image_job_dir": str(IMAGE_JOB_DIR),
        "custom_gems_path": str(CUSTOM_GEMS_PATH),
        "tool_links_path": str(TOOL_LINKS_PATH),
        "log_path": str(APP_LOG_PATH),
        "installed_models": installed_models(),
        "startup_status": st.session_state.get("startup_status", {}),
    })
    if st.button("Check Ollama Health"):
        try:
            health = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=30)
            health.raise_for_status()
            st.json(health.json())
        except Exception as exc:
            st.error(f"Ollama health check failed: {exc}")
