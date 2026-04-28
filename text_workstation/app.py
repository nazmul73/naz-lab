"""Naz Lab Phase 1.9 Text Workstation.

Stable Text Workstation for Naz Lab Phase 1.
It uses Ollama as the local LLM backend and writes outputs, logs, status,
and image job queue items to Google Drive via the shared utilities.

Phase 1.9 adds a Bangla quality guard so tiny CPU fallback models cannot silently
save broken Bangla as a successful final output.
"""

from __future__ import annotations

import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable

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

OLLAMA_GENERATE_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_HEALTH_ENDPOINT = "http://localhost:11434/api/tags"

DEFAULT_MODEL = "gemma2:2b"
CPU_FALLBACK_MODEL = "qwen2.5:0.5b"
LEGACY_MODEL = "tinyllama"
OPTIONAL_MODEL = "mistral"
AVAILABLE_MODELS = [CPU_FALLBACK_MODEL, DEFAULT_MODEL, LEGACY_MODEL, OPTIONAL_MODEL]

LENGTH_TOKEN_LIMITS = {
    "Short": 180,
    "Medium": 320,
    "Long": 520,
}
TEST_NUM_PREDICT = 80
REQUEST_TIMEOUT_SECONDS = 240

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
    "Viral Script Writer": "Turn any topic into a short-form video script with clear sections.",
    "Caption Writer": "Create platform-ready captions for any topic.",
    "Prompt Improver": "Improve visual prompts and create Image Workstation job JSON.",
}

LENGTH_INSTRUCTIONS = {
    "Short": "Keep the output concise. Use only the minimum useful text.",
    "Medium": "Use a balanced length. Include enough detail to be ready to use.",
    "Long": "Use a fuller output with more detail, while staying clean and practical.",
}

BANGLA_RANGE_RE = re.compile(r"[\u0980-\u09FF]")
BROKEN_BANGLA_MARKERS = [
    "জাতিরূপে",
    "ইকাশন",
    "ইনস্ট স্ট্যার",
    "অভিযান করল",
    "এই জাতিরূপে",
]


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


def token_limit(model: str, length: str, quick: bool = False) -> int:
    if quick:
        return TEST_NUM_PREDICT
    base = LENGTH_TOKEN_LIMITS.get(length, LENGTH_TOKEN_LIMITS["Medium"])
    if model == CPU_FALLBACK_MODEL:
        return min(base, 360)
    if model == LEGACY_MODEL:
        return min(base, 180)
    return base


def user_requested_bangla(text: str) -> bool:
    return bool(BANGLA_RANGE_RE.search(text))


def bangla_quality_score(text: str) -> int:
    score = 100
    stripped = text.strip()
    if len(stripped) < 40:
        score -= 30
    bangla_chars = len(BANGLA_RANGE_RE.findall(stripped))
    if bangla_chars < 20:
        score -= 30
    for marker in BROKEN_BANGLA_MARKERS:
        if marker in stripped:
            score -= 25
    repeated_odd = ["জাতিরূপে", "অভিযান", "ইনস্ট", "স্ট্যার"]
    for marker in repeated_odd:
        if stripped.count(marker) >= 2:
            score -= 20
    return max(score, 0)


def needs_bangla_fallback(user_input: str, output: str) -> bool:
    return user_requested_bangla(user_input) and bangla_quality_score(output) < 60


def bangla_template_output(mode: str, user_input: str) -> str:
    clean_topic = " ".join(user_input.strip().split()) or "AI tools দিয়ে ছোট ব্যবসার কনটেন্ট তৈরি"
    if mode == "Story Writer":
        return f"""Title
AI দিয়ে ছোট ব্যবসার নতুন শুরু

Setup
একজন ছোট ব্যবসায়ী প্রতিদিন কনটেন্ট বানাতে গিয়ে সমস্যায় পড়তেন। দোকান সামলানো, কাস্টমারের মেসেজের উত্তর দেওয়া, নতুন পোস্টের আইডিয়া বের করা—সব একসাথে সামলানো সহজ ছিল না।

Main Event
একদিন তিনি সিদ্ধান্ত নিলেন, কাজটা এলোমেলোভাবে না করে AI tools দিয়ে একটা সহজ পদ্ধতি বানাবেন। প্রথমে তিনি বিষয় লিখলেন: {clean_topic}। তারপর সেই বিষয় থেকে পোস্টের লেখা, ছবির ধারণা, ক্যাপশন আর ছোট ভিডিওর স্ক্রিপ্ট আলাদা করে সাজালেন।

Turning Point
আগে যে কাজ করতে অনেক সময় লাগত, এখন সেটা ধাপে ধাপে সহজ হয়ে গেল। তিনি বুঝলেন, AI শুধু নতুন টুল না; ঠিকভাবে ব্যবহার করলে এটা প্রতিদিনের কাজ গুছিয়ে দিতে পারে।

Ending
এরপর থেকে তিনি প্রতিদিন নতুন করে শুরু না করে একটি নিয়মিত workflow ব্যবহার করতে লাগলেন। এতে সময় বাঁচল, কাজ পরিষ্কার হলো, আর কনটেন্ট বানানো নিয়ে ভয়ও কমে গেল।

Question CTA
আপনি হলে আপনার ব্যবসার কোন কাজটা আগে AI দিয়ে সহজ করতেন?"""
    if mode == "Viral Script Writer":
        return f"""Title
AI দিয়ে ছোট ব্যবসার কনটেন্ট সহজ করার উপায়

Hook
প্রতিদিন কনটেন্ট বানাতে গিয়ে আটকে গেলে নতুন টুল নয়, আগে দরকার একটি সহজ workflow।

Voiceover
অনেক ছোট ব্যবসায়ী ভালো পণ্য বা সার্ভিস থাকা সত্ত্বেও নিয়মিত পোস্ট করতে পারেন না। কারণ আইডিয়া, লেখা, ছবি আর ক্যাপশন—সব একসাথে সামলানো কঠিন।

AI tools ব্যবহার করলে কাজটা ধাপে ধাপে করা যায়। প্রথমে বিষয় লিখুন: {clean_topic}। এরপর সেটাকে পোস্ট, স্ক্রিপ্ট, image prompt আর caption-এ ভাগ করুন।

এভাবে AI আপনার হয়ে ব্যবসা চালাবে না, কিন্তু আপনার কনটেন্ট planning অনেক সহজ করে দেবে।

On-screen text
AI tools + simple workflow = faster content planning

Caption
ছোট ব্যবসার কনটেন্ট বানাতে AI tools তখনই কাজে লাগে, যখন সেটাকে একটি নিয়মিত workflow-এর অংশ করা যায়।

CTA
আপনি কোন অংশটা আগে automate করতে চান?"""
    if mode == "Caption Writer":
        return f"""Caption 1
ছোট ব্যবসার কনটেন্ট বানানো কঠিন মনে হলে আগে কাজটা ছোট ছোট ধাপে ভাগ করুন। একটি বিষয় নিন, তারপর AI tools দিয়ে পোস্টের লেখা, ক্যাপশন, image prompt আর reel idea তৈরি করুন।

বিষয়: {clean_topic}

আপনি হলে কোন ধাপটা আগে automate করতেন?

Caption 2
AI tools ব্যবহার করার আসল সুবিধা হলো—এটা আপনার কাজ গুছিয়ে দিতে পারে। প্রতিদিন নতুন করে ভাবার বদলে একটি fixed workflow ব্যবহার করুন।

Caption 3
ছোট ব্যবসার জন্য নিয়মিত কনটেন্ট দরকার, কিন্তু সবসময় সময় থাকে না। AI tools দিয়ে content planning করলে কাজটা দ্রুত, সহজ এবং repeatable হয়।"""
    if mode == "Prompt Improver":
        return f"""Clean modern productivity visual of a Bangladeshi small business owner using AI tools on a laptop, organized content planning workflow visible on screen, realistic office or shop environment, natural light, premium but practical social media aesthetic, adult subject only, clear face, clean composition, Facebook-ready image.

Topic: {clean_topic}

Negative prompt: no fake logo, no watermark, no distorted face"""
    return f"""{clean_topic}

এই বিষয়টি নিয়ে একটি সহজ, পরিষ্কার এবং Facebook-ready লেখা তৈরি করা যায়। প্রথমে সমস্যাটি দেখাতে হবে, তারপর AI tools কীভাবে কাজ সহজ করে তা বোঝাতে হবে। শেষে দর্শককে এমন একটি প্রশ্ন করতে হবে, যাতে তারা নিজের অভিজ্ঞতা শেয়ার করতে পারে।

ছোট ব্যবসার জন্য সবচেয়ে বড় চ্যালেঞ্জ হলো নিয়মিত কনটেন্ট বানানো। AI tools ব্যবহার করলে বিষয় নির্বাচন, পোস্ট লেখা, ক্যাপশন তৈরি, image prompt বানানো এবং ভিডিও আইডিয়া সাজানো—সবকিছু একটি সহজ workflow-এর মধ্যে আনা যায়।

আপনি হলে আপনার কনটেন্ট তৈরির কোন অংশটা আগে AI দিয়ে সহজ করতেন?"""


def build_mode_instruction(mode: str, length: str) -> str:
    base = LENGTH_INSTRUCTIONS.get(length, LENGTH_INSTRUCTIONS["Medium"])
    strict = {
        "Free Writer": "If the user asks for a post, write a complete post, not just a title. For Bangla, use natural spoken Bangla and avoid broken, literal, or machine-translated words.",
        "Re-writer": "Return the rewritten version directly. Preserve the original meaning unless the user asks to change it. For Bangla, use natural spoken Bangla.",
        "Story Writer": "Use exactly these sections: Title, Setup, Main Event, Turning Point, Ending, Question CTA. For Bangla, use simple human language.",
        "Viral Script Writer": "Use exactly these sections: Title, Hook, Voiceover, On-screen text, Caption, CTA. For Bangla, use short natural sentences.",
        "Caption Writer": "If the user asks for captions, provide clear caption options. Use Caption 1, Caption 2, Caption 3 when multiple are useful.",
        "Prompt Improver": "Return a polished visual prompt with subject, setting, mood, lighting, camera/style, and safety constraints when relevant.",
    }.get(mode, "Answer directly in the requested format.")
    return f"{base}\n{strict}\nFinal answer only. Do not repeat instructions."


def build_prompt(user_prompt: str, system_prompt: str | None = None, extra_instruction: str | None = None) -> str:
    instruction_parts = []
    if system_prompt:
        instruction_parts.append(system_prompt)
    if extra_instruction:
        instruction_parts.append(extra_instruction)
    instruction = "\n\n".join(instruction_parts).strip()
    if not instruction:
        return f"<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    return (
        "<|im_start|>system\n"
        f"{instruction}\n"
        "Do not repeat the instruction. Write only the final answer."
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
    leak_phrases = ["You are Naz Lab", "Your job:", "Rules:", "Do not repeat", "Final answer only", "Write only the final answer"]
    if any(phrase in cleaned[:500] for phrase in leak_phrases):
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        filtered = [line for line in lines if not any(phrase in line for phrase in leak_phrases)]
        cleaned = "\n".join(filtered).strip()
    return cleaned.strip()


def call_ollama(prompt: str, model: str, system_prompt: str | None = None, timeout: int = REQUEST_TIMEOUT_SECONDS, num_predict: int = 320, extra_instruction: str | None = None) -> str:
    payload = {
        "model": model,
        "prompt": build_prompt(prompt, system_prompt, extra_instruction),
        "stream": False,
        "options": {
            "num_predict": num_predict,
            "temperature": 0.25,
            "top_p": 0.9,
            "repeat_penalty": 1.12,
            "stop": ["<|im_end|>", "<|im_start|>user", "USER:", "INSTRUCTION:", "TASK:"],
        },
    }
    response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, timeout=timeout)
    response.raise_for_status()
    return clean_model_output(response.json().get("response", ""))


def get_ollama_tags() -> dict:
    response = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=15)
    response.raise_for_status()
    return response.json()


def installed_model_names(tags: dict) -> list[str]:
    return [item.get("name") for item in tags.get("models", []) if item.get("name")]


def save_text_output(output_dir: Path, prefix: str, content: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{prefix}_{now_stamp()}.txt"
    path.write_text(content, encoding="utf-8")
    append_output_log(OUTPUT_LOG_JSON, workstation="text_workstation", event="output_saved", details={"path": str(path), "prefix": prefix})
    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": "stable", "last_output_path": str(path)})
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
    lines = [f"[{msg.get('role', 'unknown')}]\n{msg.get('content', '')}\n" for msg in messages]
    return save_text_output(CHAT_OUTPUTS, "chat", "\n".join(lines))


def render_backend_badge(model: str) -> None:
    try:
        names = installed_model_names(get_ollama_tags())
        if any(name == model or name.startswith(f"{model}:") for name in names):
            st.success(f"Backend ready. Selected model found: {model}")
        else:
            st.warning(f"Ollama is running, but selected model is not listed: {model}")
            st.caption("Run launcher again to pull the recommended model.")
    except Exception as exc:
        st.error(f"Ollama backend is not reachable: {exc}")


def render_general_chat(model: str, length: str) -> None:
    st.subheader("General Chat")
    st.caption("Normal assistant mode for planning, prompts, writing, coding help, and general questions.")
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
                    answer = call_ollama(conversation, model=model, system_prompt=system_prompt, num_predict=token_limit(model, length), extra_instruction=LENGTH_INSTRUCTIONS[length])
                    if needs_bangla_fallback(user_prompt, answer):
                        answer = bangla_template_output("Free Writer", user_prompt)
                        st.warning("Small CPU model produced low-quality Bangla. Naz Lab used safe Bangla fallback output.")
                    st.markdown(answer)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        except requests.exceptions.Timeout:
            st.error("Ollama request timed out. Use qwen2.5:0.5b on CPU or switch to T4 GPU.")
        except Exception as exc:
            st.error(f"Ollama connection error: {exc}")


def clear_mode_state(mode: str) -> None:
    for suffix in ["input", "output", "saved_path", "job_path", "status", "elapsed", "length"]:
        st.session_state.pop(state_key(mode, suffix), None)


def render_writer_mode(mode: str, model: str, global_length: str) -> None:
    config = MODE_CONFIG[mode]
    st.subheader(mode)
    st.caption(MODE_HELP.get(mode, "Accept any topic. The mode controls format, not topic."))

    input_key = state_key(mode, "input")
    output_key = state_key(mode, "output")
    saved_path_key = state_key(mode, "saved_path")
    job_path_key = state_key(mode, "job_path")
    status_key = state_key(mode, "status")
    elapsed_key = state_key(mode, "elapsed")
    length_key = state_key(mode, "length")

    for key, default in [(input_key, ""), (output_key, ""), (saved_path_key, ""), (job_path_key, ""), (status_key, "Ready"), (elapsed_key, ""), (length_key, global_length)]:
        st.session_state.setdefault(key, default)

    system_prompt = read_prompt(config["prompt_file"])
    with st.form(key=f"{state_key(mode, 'form')}"):
        user_input = st.text_area("Input context or topic", value=st.session_state[input_key], height=210, placeholder="Write any topic or task here. The selected mode controls the output format.")
        selected_length = st.radio("Output length", ["Short", "Medium", "Long"], index=["Short", "Medium", "Long"].index(st.session_state.get(length_key, global_length)), horizontal=True)
        col_a, col_b = st.columns(2)
        with col_a:
            generate_clicked = st.form_submit_button(f"Generate {mode}", use_container_width=True)
        with col_b:
            quick_clicked = st.form_submit_button("Quick Test", use_container_width=True)

    if generate_clicked or quick_clicked:
        st.session_state[input_key] = user_input
        st.session_state[length_key] = selected_length
        if not user_input.strip():
            st.warning("Please provide input first.")
            return
        try:
            st.session_state[status_key] = "Generating..."
            start = time.time()
            limit = token_limit(model, selected_length, quick_clicked)
            extra_instruction = build_mode_instruction(mode, selected_length)
            with st.spinner(f"Generating with {model}. Length: {selected_length}. Token limit: {limit}"):
                result = call_ollama(user_input, model=model, system_prompt=system_prompt, num_predict=limit, extra_instruction=extra_instruction)
            if needs_bangla_fallback(user_input, result):
                result = bangla_template_output(mode, user_input)
                st.warning("Small CPU model produced low-quality Bangla. Naz Lab used safe Bangla fallback output.")
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
            st.session_state[status_key] = "Timed out. Use Short or Medium on CPU, or switch to T4 GPU."
            st.error(st.session_state[status_key])
            return
        except requests.exceptions.ConnectionError:
            st.session_state[status_key] = "Cannot connect to Ollama. Restart launcher and refresh page."
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
    selected = st.selectbox("Select output file", [str(path) for path in files[:100]])
    if selected:
        path = Path(selected)
        st.caption(str(path))
        st.text_area("Preview", path.read_text(encoding="utf-8"), height=360)


def render_settings(model: str, length: str) -> None:
    st.subheader("Settings")
    st.caption("Verify backend, test selected model, and view persistence paths.")
    render_backend_badge(model)
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
            except Exception as exc:
                st.error(f"Selected model test failed: {exc}")
    st.markdown("### Phase 1 status")
    st.success("Text Workstation status: stable for Phase 1.9")
    st.write({"phase": "1.9", "default_cpu_model": CPU_FALLBACK_MODEL, "gpu_model": DEFAULT_MODEL, "legacy_not_recommended": LEGACY_MODEL, "selected_model": model, "selected_length": length, "bangla_quality_guard": "enabled"})
    st.markdown("### Paths")
    st.write({"base_path": str(BASE_PATH), "chat_outputs": str(CHAT_OUTPUTS), "text_outputs": str(TEXT_OUTPUTS), "script_outputs": str(SCRIPT_OUTPUTS), "image_prompts": str(IMAGE_PROMPTS), "image_jobs": str(IMAGE_JOBS), "workstation_links_json": str(WORKSTATION_LINKS_JSON), "output_log_json": str(OUTPUT_LOG_JSON)})


def render_direct_test(model: str, length: str) -> None:
    st.subheader("Direct Test")
    st.caption("Use this to isolate Ollama/model response without writer prompt files.")
    prompt = st.text_input("Test prompt", value="Write one short sentence: AI saves time.")
    if st.button("Run Direct Test"):
        try:
            start = time.time()
            answer = call_ollama(prompt, model=model, timeout=120, num_predict=token_limit(model, length, quick=True))
            st.success(f"Direct test completed in {round(time.time() - start, 2)}s")
            st.code(answer or "[empty response]")
        except Exception as exc:
            st.error(f"Direct test failed: {exc}")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Text Workstation", page_icon="✍️", layout="wide")
    st.title("✍️ Naz Lab Text Workstation")
    st.caption("Phase 1.9 stable: output length control, Bangla quality guard, qwen CPU fallback, Drive persistence.")
    missing = ensure_phase_0_ready()
    if missing:
        st.error("Phase 0 foundation appears incomplete. Run master_setup/init_drive_structure.py first.")
        st.code("\n".join(missing))
        return
    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": "stable", "phase": "1.9", "last_seen": datetime.now().isoformat(timespec="seconds")})
    with st.sidebar:
        st.header("Naz Lab Core")
        model = st.selectbox("Model", AVAILABLE_MODELS, index=0, key="selected_model")
        global_length = st.selectbox("Default output length", ["Short", "Medium", "Long"], index=1, key="global_output_length")
        page = st.radio("Mode", ["General Chat", "Free Writer", "Re-writer", "Story Writer", "Viral Script Writer", "Caption Writer", "Prompt Improver", "Output Library", "Settings", "Direct Test"], key="selected_page")
        if model == CPU_FALLBACK_MODEL:
            st.info("CPU fallback selected. Bangla quality guard is active.")
        elif model == LEGACY_MODEL:
            st.warning("tinyllama is legacy and not recommended for writing quality.")
        elif model == DEFAULT_MODEL:
            st.info("Best default for T4/GPU runtime.")
        st.caption("Text Workstation Phase 1.9 stable.")
    if page == "General Chat":
        render_general_chat(model, global_length)
    elif page in MODE_CONFIG:
        render_writer_mode(page, model, global_length)
    elif page == "Output Library":
        render_output_library()
    elif page == "Settings":
        render_settings(model, global_length)
    elif page == "Direct Test":
        render_direct_test(model, global_length)


if __name__ == "__main__":
    main()
