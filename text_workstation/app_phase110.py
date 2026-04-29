"""Naz Lab Text Workstation Phase 1.10.

CPU-stable Text Workstation with:
- qwen2.5:1.5b as the recommended CPU model
- qwen2.5:0.5b as emergency fallback only
- Bangla Safe Mode default
- template-first fallback for structured Bangla content modes
- controlled text output save to Drive
- Image Job JSON creation for Image Workstation handoff
"""

from __future__ import annotations

import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

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
from shared.json_utils import append_output_log, safe_write_json, update_workstation_status  # noqa: E402

PHASE = "1.10"
PHASE_STATUS = "stable-bangla-safe-mode-qwen-1-5b"
OLLAMA_GENERATE_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_HEALTH_ENDPOINT = "http://localhost:11434/api/tags"

CPU_RECOMMENDED_MODEL = "qwen2.5:1.5b"
CPU_EMERGENCY_MODEL = "qwen2.5:0.5b"
GPU_RECOMMENDED_MODEL = "gemma2:2b"
OPTIONAL_MODEL = "qwen2.5:3b"
AVAILABLE_MODELS = [CPU_RECOMMENDED_MODEL, GPU_RECOMMENDED_MODEL, OPTIONAL_MODEL, CPU_EMERGENCY_MODEL]

MODE_CONFIG = {
    "General Chat": {"output_dir": CHAT_OUTPUTS, "prefix": "general_chat", "auto_save": False, "template_default": False},
    "Free Writer": {"output_dir": TEXT_OUTPUTS, "prefix": "free_writer", "auto_save": False, "template_default": False},
    "Story Writer": {"output_dir": TEXT_OUTPUTS, "prefix": "story_writer", "auto_save": True, "template_default": True},
    "Viral Script Writer": {"output_dir": SCRIPT_OUTPUTS, "prefix": "viral_script_writer", "auto_save": True, "template_default": True},
    "Caption Writer": {"output_dir": TEXT_OUTPUTS, "prefix": "caption_writer", "auto_save": False, "template_default": True},
    "Prompt Improver": {"output_dir": IMAGE_PROMPTS, "prefix": "prompt_improver", "auto_save": False, "template_default": True},
    "YouTube Script": {"output_dir": SCRIPT_OUTPUTS, "prefix": "youtube_script", "auto_save": False, "template_default": True},
}

LENGTH_TOKEN_LIMITS = {"Short": 220, "Medium": 420, "Long": 650}
REQUEST_TIMEOUT_SECONDS = 300
DEFAULT_NEGATIVE_PROMPT = "no fake logo, no watermark, no distorted face"
BANGLA_RE = re.compile(r"[\u0980-\u09FF]")
BROKEN_MARKERS = ["জাতিরূপে", "ইকাশন", "ইনস্ট স্ট্যার", "অভিমান করে ফেলল", "এই জাতিরূপে", "অভিযান করল"]


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")[:80] or "naz_lab"


def ensure_dirs() -> None:
    for folder in [BASE_PATH, CHAT_OUTPUTS, TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS, IMAGE_JOBS, WORKSTATION_LINKS_JSON.parent, OUTPUT_LOG_JSON.parent]:
        folder.mkdir(parents=True, exist_ok=True)
    if not WORKSTATION_LINKS_JSON.exists():
        safe_write_json(WORKSTATION_LINKS_JSON, {})
    if not OUTPUT_LOG_JSON.exists():
        safe_write_json(OUTPUT_LOG_JSON, {"logs": []})


def user_requested_bangla(text: str, language: str) -> bool:
    return language != "English" or bool(BANGLA_RE.search(text))


def bangla_quality_score(text: str) -> int:
    stripped = text.strip()
    score = 100
    if len(stripped) < 60:
        score -= 25
    if len(BANGLA_RE.findall(stripped)) < 25:
        score -= 30
    for marker in BROKEN_MARKERS:
        if marker in stripped:
            score -= 30
    odd_terms = ["জাতিরূপে", "ইকাশন", "স্ট্যার", "অভিমান"]
    for marker in odd_terms:
        if stripped.count(marker) >= 1:
            score -= 15
    return max(score, 0)


def needs_safe_bangla(user_input: str, language: str, output: str, bangla_safe_mode: bool) -> bool:
    if not bangla_safe_mode:
        return False
    if not user_requested_bangla(user_input, language):
        return False
    return bangla_quality_score(output) < 70


def template_chat(topic: str) -> str:
    return f"""আপনি লিখেছেন: {topic}

আমি বিষয়টা বুঝেছি। আপনি চাইলে এটাকে পোস্ট, স্ক্রিপ্ট, ক্যাপশন, গল্প, image prompt অথবা content package workflow-তে রূপ দিতে পারেন।

এই ইনপুট নিয়ে এখন কোন ধরনের আউটপুট চান?"""


def template_story(topic: str) -> str:
    return f"""Title
AI দিয়ে ছোট ব্যবসার নতুন শুরু

Setup
একজন ছোট ব্যবসায়ী প্রতিদিন কনটেন্ট বানাতে গিয়ে সমস্যায় পড়তেন। দোকান সামলানো, কাস্টমারের মেসেজের উত্তর দেওয়া, নতুন পোস্টের আইডিয়া বের করা—সব একসাথে সামলানো সহজ ছিল না।

Main Event
একদিন তিনি সিদ্ধান্ত নিলেন, কাজটা এলোমেলোভাবে না করে AI tools দিয়ে একটি সহজ workflow বানাবেন। বিষয় ছিল: {topic}। তিনি প্রথমে বিষয় লিখলেন, তারপর সেটাকে পোস্টের লেখা, ছবির ধারণা, ক্যাপশন আর ছোট ভিডিওর স্ক্রিপ্টে ভাগ করলেন।

Turning Point
আগে যে কাজ করতে অনেক সময় লাগত, এখন সেটা ধাপে ধাপে সহজ হয়ে গেল। তিনি বুঝলেন, AI শুধু নতুন টুল না; ঠিকভাবে ব্যবহার করলে এটা প্রতিদিনের কাজ গুছিয়ে দিতে পারে।

Ending
এরপর থেকে তিনি প্রতিদিন নতুন করে শুরু না করে একটি নিয়মিত পদ্ধতি ব্যবহার করতে লাগলেন। এতে সময় বাঁচল, কাজ পরিষ্কার হলো, আর কনটেন্ট বানানো নিয়ে ভয়ও কমে গেল।

Question CTA
আপনি হলে আপনার ব্যবসার কোন কাজটা আগে AI দিয়ে সহজ করতেন?"""


def template_script(topic: str) -> str:
    return f"""Title
AI দিয়ে ছোট ব্যবসার কনটেন্ট সহজ করার উপায়

Hook
প্রতিদিন কনটেন্ট বানাতে গিয়ে আটকে গেলে নতুন টুল নয়, আগে দরকার একটি সহজ workflow।

Voiceover
অনেক ছোট ব্যবসায়ী ভালো পণ্য বা সার্ভিস থাকা সত্ত্বেও নিয়মিত পোস্ট করতে পারেন না। কারণ আইডিয়া, লেখা, ছবি আর ক্যাপশন—সব একসাথে সামলানো কঠিন।

AI tools ব্যবহার করলে কাজটা ধাপে ধাপে করা যায়। প্রথমে বিষয় লিখুন: {topic}। এরপর সেটাকে পোস্ট, স্ক্রিপ্ট, image prompt আর caption-এ ভাগ করুন।

এভাবে AI আপনার হয়ে ব্যবসা চালাবে না, কিন্তু আপনার content planning অনেক সহজ করে দেবে।

On-screen text
AI tools + simple workflow = faster content planning

Caption
ছোট ব্যবসার কনটেন্ট বানাতে AI tools তখনই কাজে লাগে, যখন সেটাকে একটি নিয়মিত workflow-এর অংশ করা যায়।

CTA
আপনি কোন অংশটা আগে automate করতে চান?"""


def template_youtube_script(topic: str) -> str:
    return f"""Title
{topic}

Intro Hook
আজকের ভিডিওতে আমরা সহজভাবে দেখব—এই বিষয়টা কেন গুরুত্বপূর্ণ এবং কীভাবে এটাকে বাস্তবে কাজে লাগানো যায়।

Main Points
১. সমস্যাটা কী
অনেক সময় আমরা কাজ শুরু করি, কিন্তু পরিষ্কার কাঠামো না থাকলে মাঝপথে আটকে যাই।

২. সমাধানের সহজ পথ
প্রথমে বিষয়টা ছোট ধাপে ভাগ করুন। তারপর প্রতিটি ধাপের জন্য আলাদা content, visual, caption এবং action plan তৈরি করুন।

৩. ব্যবহারিক উদাহরণ
ধরুন আপনার বিষয় হলো: {topic}। এটাকে একটি hook, তিনটি main point, একটি example এবং একটি CTA-তে ভাগ করলে ভিডিও বানানো সহজ হয়।

Closing CTA
এই ধরনের workflow আপনার কাজে লাগবে মনে হলে, পরের ভিডিওতে কোন বিষয় চান?"""


def template_caption(topic: str) -> str:
    return f"""Caption 1
ছোট ব্যবসার কনটেন্ট বানানো কঠিন মনে হলে আগে কাজটা ছোট ছোট ধাপে ভাগ করুন। একটি বিষয় নিন, তারপর AI tools দিয়ে পোস্টের লেখা, ক্যাপশন, image prompt আর reel idea তৈরি করুন।

বিষয়: {topic}

আপনি হলে কোন ধাপটা আগে automate করতেন?

Caption 2
AI tools ব্যবহার করার আসল সুবিধা হলো—এটা আপনার কাজ গুছিয়ে দিতে পারে। প্রতিদিন নতুন করে ভাবার বদলে একটি fixed workflow ব্যবহার করুন।

Caption 3
ছোট ব্যবসার জন্য নিয়মিত কনটেন্ট দরকার, কিন্তু সবসময় সময় থাকে না। AI tools দিয়ে content planning করলে কাজটা দ্রুত, সহজ এবং repeatable হয়।"""


def template_prompt(topic: str) -> str:
    return f"""Clean modern productivity visual of a Bangladeshi small business owner using AI tools on a laptop, organized content planning workflow visible on screen, realistic office or shop environment, natural light, premium but practical social media aesthetic, adult subject only, clear face, clean composition, Facebook-ready image.

Topic: {topic}

Negative prompt: {DEFAULT_NEGATIVE_PROMPT}"""


def template_free(topic: str) -> str:
    return f"""{topic}

ছোট ব্যবসার জন্য নিয়মিত কনটেন্ট বানানো অনেক সময় কঠিন হয়ে যায়। প্রতিদিন নতুন আইডিয়া বের করা, পোস্ট লেখা, ক্যাপশন বানানো, ছবির ধারণা তৈরি করা—সবকিছু একসাথে করলে কাজটা ভারী লাগে।

AI tools ব্যবহার করলে এই কাজগুলো ধাপে ধাপে সহজ করা যায়। প্রথমে একটি বিষয় ঠিক করুন। তারপর সেই বিষয় থেকে পোস্টের লেখা, image prompt, caption এবং ছোট ভিডিওর idea তৈরি করুন।

এভাবে AI আপনার জায়গায় ব্যবসা চালাবে না, কিন্তু আপনার planning দ্রুত ও পরিষ্কার করে দেবে।

আপনি হলে আপনার content workflow-এর কোন অংশটা আগে automate করতেন?"""


def template_output(mode: str, topic: str) -> str:
    clean_topic = " ".join(topic.strip().split()) or "AI tools দিয়ে ছোট ব্যবসার content planning"
    if mode == "General Chat":
        return template_chat(clean_topic)
    if mode == "Story Writer":
        return template_story(clean_topic)
    if mode == "Viral Script Writer":
        return template_script(clean_topic)
    if mode == "YouTube Script":
        return template_youtube_script(clean_topic)
    if mode == "Caption Writer":
        return template_caption(clean_topic)
    if mode == "Prompt Improver":
        return template_prompt(clean_topic)
    return template_free(clean_topic)


def build_system_instruction(mode: str, language: str, length: str, bangla_safe_mode: bool) -> str:
    lang_rule = "Write in natural, simple Bangla." if language != "English" else "Write in clear English."
    safe_rule = "Bangla Safe Mode is ON: avoid broken, literal, machine-translated Bangla. Use short natural Bangla sentences." if bangla_safe_mode else ""
    structure = {
        "General Chat": "Reply conversationally and directly. Do not save or format as a file unless asked.",
        "Free Writer": "Write a complete ready-to-use post or content draft.",
        "Story Writer": "Use exactly: Title, Setup, Main Event, Turning Point, Ending, Question CTA.",
        "Viral Script Writer": "Use exactly: Title, Hook, Voiceover, On-screen text, Caption, CTA.",
        "YouTube Script": "Use exactly: Title, Intro Hook, Main Points, Example, Closing CTA.",
        "Caption Writer": "Write Caption 1, Caption 2, Caption 3.",
        "Prompt Improver": "Write one polished visual prompt and one negative prompt.",
    }.get(mode, "Write the final output directly.")
    return "\n".join([
        "You are Naz Lab Text Workstation Phase 1.10.",
        lang_rule,
        safe_rule,
        structure,
        f"Length: {length}.",
        "Return final output only. Do not repeat instructions.",
    ]).strip()


def call_ollama(user_prompt: str, model: str, mode: str, language: str, length: str, bangla_safe_mode: bool) -> str:
    system_instruction = build_system_instruction(mode, language, length, bangla_safe_mode)
    prompt = f"<|im_start|>system\n{system_instruction}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": LENGTH_TOKEN_LIMITS.get(length, 420),
            "temperature": 0.22,
            "top_p": 0.85,
            "repeat_penalty": 1.15,
            "stop": ["<|im_end|>", "<|im_start|>user", "INSTRUCTION:", "TASK:"],
        },
    }
    response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return str(response.json().get("response", "")).strip().replace("<|im_end|>", "").strip()


def get_ollama_tags() -> dict[str, Any]:
    response = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=15)
    response.raise_for_status()
    return response.json()


def installed_model_names() -> list[str]:
    try:
        tags = get_ollama_tags()
        return [item.get("name", "") for item in tags.get("models", []) if item.get("name")]
    except Exception:
        return []


def model_installed(model: str) -> bool:
    return any(name == model or name.startswith(f"{model}:") for name in installed_model_names())


def save_text_output(mode: str, project: str, language: str, topic: str, content: str, engine_status: str) -> Path:
    config = MODE_CONFIG.get(mode, MODE_CONFIG["Free Writer"])
    output_dir = config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{config['prefix']}_{safe_slug(project)}_{safe_slug(topic)}_{now_stamp()}.txt"
    header = {
        "phase": PHASE,
        "project": project,
        "mode": mode,
        "language": language,
        "topic": topic,
        "engine_status": engine_status,
        "created_at": now_iso(),
    }
    path.write_text("# Naz Lab Text Output\n\n```json\n" + json.dumps(header, ensure_ascii=False, indent=2) + "\n```\n\n" + content, encoding="utf-8")
    append_output_log(OUTPUT_LOG_JSON, workstation="text_workstation", event="output_saved", details={"path": str(path), "mode": mode, "engine_status": engine_status})
    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": PHASE_STATUS, "phase": PHASE, "last_output_path": str(path)})
    return path


def create_image_job(project: str, mode: str, topic: str, prompt_text: str, source_path: Path | None) -> Path:
    IMAGE_JOBS.mkdir(parents=True, exist_ok=True)
    job_id = f"image_{uuid.uuid4().hex[:10]}"
    path = IMAGE_JOBS / f"image_job_{safe_slug(project)}_{now_stamp()}_{job_id}.json"
    data = {
        "job_id": job_id,
        "schema_version": "1.10",
        "source_workstation": "text_workstation",
        "target_workstation": "image_workstation",
        "source_mode": mode,
        "status": "queued",
        "review_status": "pending",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "project": project,
        "topic": topic,
        "input_payload": {
            "positive_prompt": prompt_text,
            "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
            "format": "1:1 square by default; adapt to 9:16 for reels when requested",
        },
        "source_text_path": str(source_path) if source_path else "",
        "output_path": "",
        "errors": [],
    }
    safe_write_json(path, data)
    append_output_log(OUTPUT_LOG_JSON, workstation="text_workstation", event="image_job_created", details={"path": str(path), "job_id": job_id})
    return path


def render_status_panel(model: str) -> None:
    st.subheader("Backend status")
    names = installed_model_names()
    c1, c2, c3 = st.columns(3)
    c1.metric("Phase", PHASE)
    c2.metric("Selected model installed", "yes" if model_installed(model) else "no")
    c3.metric("Installed models", len(names))
    st.write({
        "recommended_cpu_model": CPU_RECOMMENDED_MODEL,
        "emergency_cpu_model": CPU_EMERGENCY_MODEL,
        "recommended_gpu_model": GPU_RECOMMENDED_MODEL,
        "installed_models": names,
        "base_path": str(BASE_PATH),
        "chat_outputs": str(CHAT_OUTPUTS),
        "text_outputs": str(TEXT_OUTPUTS),
        "script_outputs": str(SCRIPT_OUTPUTS),
        "image_jobs": str(IMAGE_JOBS),
        "bangla_safe_mode": "default on",
        "mode_config": MODE_CONFIG,
    })
    if not model_installed(model):
        st.warning(f"Selected model is not installed: {model}. Run launcher model pull or select an installed model.")


def safe_json_read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def render_builder() -> None:
    st.header("Text Builder")
    col1, col2, col3 = st.columns(3)
    mode_names = list(MODE_CONFIG.keys())
    with col1:
        project = st.selectbox("Project", ["General Bangla", "True Noir Tales", "ToolFlow", "Custom"], index=0)
        mode = st.selectbox("Mode", mode_names, index=mode_names.index("Free Writer"))
    with col2:
        language = st.selectbox("Language", ["Bangla", "English", "Mixed Bangla-English"], index=0)
        model = st.selectbox("Model", AVAILABLE_MODELS, index=0)
    with col3:
        length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)
        bangla_safe_mode = st.checkbox("Bangla Safe Mode", value=True)

    topic = st.text_area("Topic / input", value="একজন ছোট ব্যবসায়ী AI tools ব্যবহার করে প্রতিদিনের content planning সহজ করে ফেলল।", height=140)
    config = MODE_CONFIG.get(mode, MODE_CONFIG["Free Writer"])
    template_first = st.checkbox("Template-first / structured fallback", value=bool(config.get("template_default", False)), help="Default ON only for structured modes. General Chat and Free Writer default OFF.")

    if "last_output" not in st.session_state:
        st.session_state.last_output = ""
        st.session_state.last_saved_path = ""
        st.session_state.last_engine_status = ""

    c1, c2, c3 = st.columns(3)
    generate = c1.button("Generate", type="primary", use_container_width=True)
    save = c2.button("Save current output", use_container_width=True)
    send_image = c3.button("Send to Image Workstation", use_container_width=True)

    if generate:
        engine_status = "template"
        if template_first and user_requested_bangla(topic, language):
            result = template_output(mode, topic)
            engine_status = "bangla_safe_template_first"
        else:
            try:
                with st.spinner(f"Generating with {model}..."):
                    result = call_ollama(topic, model, mode, language, length, bangla_safe_mode)
                engine_status = f"ollama:{model}"
                if needs_safe_bangla(topic, language, result, bangla_safe_mode):
                    result = template_output(mode, topic)
                    engine_status = f"bangla_safe_template_after_low_quality_model:{model}"
                    st.warning("Model output failed Bangla quality guard. Safe Bangla template was used.")
            except requests.exceptions.ConnectionError:
                result = template_output(mode, topic)
                engine_status = "template_after_ollama_connection_error"
                st.warning("Ollama connection failed. Safe template output was used.")
            except requests.exceptions.Timeout:
                result = template_output(mode, topic)
                engine_status = "template_after_ollama_timeout"
                st.warning("Ollama timed out. Safe template output was used.")
            except Exception as exc:
                result = template_output(mode, topic)
                engine_status = f"template_after_error:{type(exc).__name__}"
                st.warning(f"Model generation failed. Safe template output was used. Error: {exc}")
        st.session_state.last_output = result
        st.session_state.last_engine_status = engine_status
        if bool(config.get("auto_save", False)):
            saved_path = save_text_output(mode, project, language, topic, result, engine_status)
            st.session_state.last_saved_path = str(saved_path)
            st.success(f"Generated and auto-saved: {saved_path}")
        else:
            st.session_state.last_saved_path = ""
            st.success("Generated. Output is displayed below. Not auto-saved; press Save current output only if needed.")

    output_text = st.text_area("Output", value=st.session_state.last_output, height=420)
    st.session_state.last_output = output_text
    if st.session_state.last_engine_status:
        st.caption(f"Engine status: {st.session_state.last_engine_status}")
    if st.session_state.last_saved_path:
        st.success(f"Last saved: {st.session_state.last_saved_path}")

    if save:
        if not output_text.strip():
            st.error("No output to save.")
        else:
            saved_path = save_text_output(mode, project, language, topic, output_text, st.session_state.last_engine_status or "manual_save")
            st.session_state.last_saved_path = str(saved_path)
            st.success(f"Saved: {saved_path}")

    if send_image:
        if not output_text.strip():
            st.error("No output to send.")
        else:
            source = Path(st.session_state.last_saved_path) if st.session_state.last_saved_path else None
            image_prompt = output_text if mode == "Prompt Improver" else template_prompt(topic + "\n" + output_text[:500])
            job = create_image_job(project, mode, topic, image_prompt, source)
            st.success(f"Image job created: {job}")
            st.json(safe_json_read(job))


def render_output_library() -> None:
    st.header("Output Library")
    files: list[Path] = []
    for folder in [CHAT_OUTPUTS, TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS, IMAGE_JOBS]:
        if folder.exists():
            files.extend([path for path in folder.rglob("*") if path.is_file()])
    files = sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[:200]
    if not files:
        st.info("No outputs yet.")
        return
    selected = Path(st.selectbox("Open output/job", [str(path) for path in files]))
    st.caption(str(selected))
    st.text_area("Preview", selected.read_text(encoding="utf-8", errors="ignore"), height=420)


def main() -> None:
    st.set_page_config(page_title="Naz Lab Text Workstation", page_icon="✍️", layout="wide")
    ensure_dirs()
    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": now_iso()})
    st.title("✍️ Naz Lab Text Workstation")
    st.caption("Phase 1.10 — qwen2.5:1.5b, Bangla Safe Mode default, controlled save policy, Drive save, Image Job JSON handoff")

    with st.sidebar:
        page = st.radio("Section", ["Text Builder", "Backend Status", "Output Library"], index=0)
        st.info("Recommended CPU model: qwen2.5:1.5b. Emergency only: qwen2.5:0.5b.")

    if page == "Text Builder":
        render_builder()
    elif page == "Backend Status":
        model = st.selectbox("Check model", AVAILABLE_MODELS, index=0)
        render_status_panel(model)
    else:
        render_output_library()


if __name__ == "__main__":
    main()
