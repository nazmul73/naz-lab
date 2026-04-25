import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(page_title="Naz Lab AI Workstation", page_icon="🧪", layout="wide")

BASE_DIR = Path("/content/drive/MyDrive/NazLab")
OUTPUT_DIR = BASE_DIR / "outputs"
CONFIG_DIR = BASE_DIR / "config"
CUSTOM_GEMS_PATH = CONFIG_DIR / "custom_gems.json"
TOOL_LINKS_PATH = CONFIG_DIR / "tool_links.json"
TEXT_JOB_DIR = BASE_DIR / "text_jobs"
IMAGE_JOB_DIR = BASE_DIR / "image_jobs"
VOICE_JOB_DIR = BASE_DIR / "voice_jobs"
VIDEO_JOB_DIR = BASE_DIR / "video_jobs"
IMAGE_OUTPUT_DIR = BASE_DIR / "image_outputs"
VOICE_OUTPUT_DIR = BASE_DIR / "voice_outputs"
FACEFUSION_OUTPUT_DIR = BASE_DIR / "facefusion_outputs"
LIVEPORTRAIT_OUTPUT_DIR = BASE_DIR / "liveportrait_outputs"

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_HEALTH_ENDPOINT = "http://localhost:11434/api/tags"

GENERAL_CHAT_SYSTEM_PROMPT = """You are Naz Lab General Assistant.
You are a helpful, conversational AI assistant for Nazmul.
You can discuss any topic the user asks about, including content creation, AI tools, coding, Colab errors, business, productivity, Facebook growth, writing, prompts, and general knowledge.
Answer naturally in the user's language.
If the user writes Bangla, reply in Bangla.
If the user writes English, reply in English.
Do not restrict yourself to one content task.
Ask clarifying questions only when needed.
When the user's prompt is weak, vague, or missing important details, teach the user how to improve the prompt and provide a better prompt version."""

for folder in [
    BASE_DIR,
    OUTPUT_DIR,
    CONFIG_DIR,
    TEXT_JOB_DIR,
    IMAGE_JOB_DIR,
    VOICE_JOB_DIR,
    VIDEO_JOB_DIR,
    IMAGE_OUTPUT_DIR,
    VOICE_OUTPUT_DIR,
    FACEFUSION_OUTPUT_DIR,
    LIVEPORTRAIT_OUTPUT_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)

DEFAULT_GEMS = {
    "📖 Storyteller": {
        "description": "আবেগপূর্ণ গল্প লেখার জন্য।",
        "system_prompt": """You are Naz Lab Storyteller.
Write emotional, cinematic, human-like Bangla stories.
Use simple Bangla.
Use short paragraphs.
Avoid robotic language.""",
    },
    "📱 Viral Scripter": {
        "description": "Facebook Reel / YouTube Shorts script লেখার জন্য।",
        "system_prompt": """You are Naz Lab Viral Scripter.
Create short-form video scripts in simple Bangla.
Always include:
1. Title
2. Hook
3. Voiceover
4. On-screen text
5. Caption
6. CTA""",
    },
    "🎬 Video Planner": {
        "description": "Story থেকে scene-wise video plan বানানোর জন্য।",
        "system_prompt": """You are Naz Lab Video Planner.
Create scene-wise video plans for short-form reels.
Always include:
Scene number, visual, camera movement, lighting, mood, image prompt, video prompt, voiceover line.""",
    },
    "💼 Business Guru": {
        "description": "Marketing, ad copy, customer reply-এর জন্য।",
        "system_prompt": """You are Naz Lab Business Guru.
Write practical marketing copy, ad copy, customer replies, and business strategy.
Be clear, direct, and useful.
Avoid fake income claims.""",
    },
}


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def read_json(path: Path, default):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
        return default
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return default
        return json.loads(raw)
    except Exception:
        backup = path.with_name(f"{path.stem}_corrupted_{now_stamp()}{path.suffix}")
        try:
            path.rename(backup)
            st.warning(f"Corrupted JSON backed up to: {backup}")
        except Exception as exc:
            st.warning(f"Could not back up corrupted JSON: {exc}")
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_custom_gems():
    data = read_json(CUSTOM_GEMS_PATH, [])
    return data if isinstance(data, list) else []


def load_tool_links():
    data = read_json(TOOL_LINKS_PATH, {})
    return data if isinstance(data, dict) else {}


def save_tool_link(tool_name: str, public_link: str):
    links = load_tool_links()
    links[tool_name] = {"public_link": public_link, "updated_at": now_stamp()}
    write_json(TOOL_LINKS_PATH, links)


def merged_gems():
    gems = dict(DEFAULT_GEMS)
    for gem in load_custom_gems():
        display_name = gem.get("display_name") or f"{gem.get('emoji', '').strip()} {gem.get('name', '').strip()}".strip()
        if display_name:
            gems[display_name] = {
                "description": gem.get("description", "Custom Naz Gem"),
                "system_prompt": gem.get("system_prompt", ""),
            }
    return gems


def generate_with_ollama(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    full_prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}\n\nOUTPUT:\n"
    return call_ollama(model, full_prompt, temperature)


def call_ollama(model: str, full_prompt: str, temperature: float) -> str:
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=300)
        response.raise_for_status()
        return response.json().get("response", "No response received.")
    except requests.exceptions.ConnectionError:
        return "ERROR: Ollama server is not running. Run the Ollama serve cell again."
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out. Try a shorter prompt."
    except requests.exceptions.HTTPError as exc:
        if "model" in str(exc).lower():
            return f"ERROR: Model may not be available. Pull the model first. Details: {exc}"
        return f"ERROR: Ollama request failed: {exc}"
    except Exception as exc:
        return f"ERROR: {exc}"


def build_chat_prompt(messages):
    lines = [f"SYSTEM:\n{GENERAL_CHAT_SYSTEM_PROMPT}\n"]
    for message in messages:
        role = message.get("role", "user").upper()
        content = message.get("content", "")
        lines.append(f"{role}:\n{content}\n")
    lines.append("ASSISTANT:\n")
    return "\n".join(lines)


def save_text_output(agent: str, model: str, prompt: str, output: str):
    path = OUTPUT_DIR / f"naz_lab_{now_stamp()}.txt"
    content = (
        "NAZ LAB OUTPUT\n"
        + "=" * 40
        + f"\n\nAgent: {agent}\nModel: {model}\nTimestamp: {now_stamp()}\n\nPROMPT:\n{prompt}\n\nOUTPUT:\n{output}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def save_chat_transcript(messages, model: str):
    path = OUTPUT_DIR / f"naz_lab_chat_{now_stamp()}.txt"
    lines = ["NAZ LAB GENERAL CHAT", "=" * 40, f"Model: {model}", f"Timestamp: {now_stamp()}", ""]
    for message in messages:
        role = message.get("role", "user").upper()
        content = message.get("content", "")
        lines.append(f"{role}:\n{content}\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def save_job(job_dir: Path, tool_name: str, planned_inputs: dict, notes: str, status: str, public_link: str = ""):
    job_dir.mkdir(parents=True, exist_ok=True)
    path = job_dir / f"{tool_name.lower().replace(' ', '_')}_job_{now_stamp()}.json"
    data = {
        "tool_name": tool_name,
        "timestamp": now_stamp(),
        "planned_inputs": planned_inputs,
        "notes": notes,
        "status": status,
        "public_link_if_available": public_link,
    }
    write_json(path, data)
    return path


def tool_card(title, purpose, status, output_dir, fields, job_dir, safety_note=None):
    st.subheader(title)
    st.write(purpose)
    st.caption(f"Status: {status}")
    st.code(str(output_dir))
    values = {}
    for label, default in fields.items():
        values[label] = st.text_input(label, value=default, key=f"{title}_{label}")
    notes = st.text_area("Notes", key=f"{title}_notes")
    public_link = st.text_input("Public tool link", key=f"{title}_link")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"Save {title} public link", key=f"{title}_save_link"):
            save_tool_link(title, public_link)
            st.success(f"Saved {title} link")
    with c2:
        if st.button(f"Save {title} job plan", key=f"{title}_save_job"):
            job_path = save_job(job_dir, title, values, notes, status, public_link)
            st.success(f"Saved job plan: {job_path}")
    if safety_note:
        st.warning(safety_note)


if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "আমি Naz Lab General Assistant. আপনি যেকোনো বিষয়ে কথা বলতে পারেন—content, coding, Colab error, business, prompt, planning বা general প্রশ্ন।",
        }
    ]

st.title("🧪 Naz Lab AI Workstation")
st.caption("Free AI content workstation: Chat, Story, Script, Custom Gems, Image Tools, Voice Tools, Video Tools, and Final Content Planning.")

with st.sidebar:
    st.header("Naz Lab Control")
    model = st.selectbox("Model", ["gemma2:2b", "mistral"])
    temperature = st.slider("Creativity", min_value=0.1, max_value=1.5, value=0.8, step=0.1)
    all_gems = merged_gems()
    selected_gem = st.selectbox("Naz Gem", list(all_gems.keys()))

tabs = st.tabs(["Chat", "AI Agents", "Custom Gems", "Image Tools", "Voice Tools", "Video Tools", "Output Library", "Settings"])

with tabs[0]:
    st.header("General Chat")
    st.write("Normal assistant mode. Ask anything: content, coding, Colab errors, business, prompts, planning, or general questions.")

    clear_col, save_col = st.columns(2)
    with clear_col:
        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()
    with save_col:
        if st.button("Save Chat"):
            try:
                chat_path = save_chat_transcript(st.session_state.chat_messages, model)
                st.success(f"Saved chat: {chat_path}")
            except Exception as exc:
                st.error(f"Chat save failed: {exc}")

    for message in st.session_state.chat_messages:
        with st.chat_message(message.get("role", "assistant")):
            st.write(message.get("content", ""))

    user_message = st.chat_input("Message Naz Lab...")
    if user_message:
        st.session_state.chat_messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.write(user_message)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_prompt = build_chat_prompt(st.session_state.chat_messages)
                assistant_reply = call_ollama(model, full_prompt, temperature)
                st.write(assistant_reply)

        st.session_state.chat_messages.append({"role": "assistant", "content": assistant_reply})

with tabs[1]:
    st.header("AI Agents")
    gem = all_gems[selected_gem]
    st.info(gem.get("description", ""))
    prompt = st.text_area("Write your instruction", height=240, placeholder="একটি ৬০ সেকেন্ডের Facebook Reel script লিখো...")
    if st.button("Generate"):
        if not prompt.strip():
            st.warning("Please write a prompt first.")
        else:
            with st.spinner("Naz Lab is generating..."):
                output = generate_with_ollama(model, gem.get("system_prompt", ""), prompt, temperature)
            st.subheader("Output")
            st.write(output)
            try:
                saved_path = save_text_output(selected_gem, model, prompt, output)
                st.success(f"Saved: {saved_path}")
            except Exception as exc:
                st.error(f"Save failed: {exc}")
            st.download_button("Download Output", output, file_name="naz_lab_output.txt", mime="text/plain")

with tabs[2]:
    st.header("Custom Gems")
    st.write("Create new specialist Naz Gems without editing code.")
    with st.form("custom_gem_form"):
        emoji = st.text_input("Emoji/icon", "🕵️")
        name = st.text_input("Gem name", "True Crime Writer")
        description = st.text_area("Description", "Bangla true crime content writer")
        system_prompt = st.text_area("System prompt", "Write cinematic Bangla content with clear structure and ethical limits.")
        category = st.text_input("Category", "Content")
        output_notes = st.text_area("Output format notes", "Title, hook, body, caption")
        submitted = st.form_submit_button("Save Custom Gem")
    if submitted:
        gems = load_custom_gems()
        display_name = f"{emoji.strip()} {name.strip()}".strip()
        gems.append(
            {
                "id": str(uuid.uuid4()),
                "name": name,
                "emoji": emoji,
                "display_name": display_name,
                "description": description,
                "system_prompt": system_prompt,
                "category": category,
                "output_format_notes": output_notes,
                "created_at": now_stamp(),
            }
        )
        write_json(CUSTOM_GEMS_PATH, gems)
        st.success(f"Saved custom gem: {display_name}")
    st.subheader("Saved Custom Gems")
    custom_gems = load_custom_gems()
    if not custom_gems:
        st.info("No custom gems saved yet. Examples: 🕵️ True Crime Writer, 🖼️ Image Prompt Engineer, 🎙️ Voiceover Script Doctor, 🧩 Final Reel Pack Builder")
    else:
        for gem in custom_gems:
            with st.expander(gem.get("display_name", gem.get("name", "Custom Gem"))):
                st.write(gem.get("description", ""))
                st.code(gem.get("system_prompt", ""))
                if st.button("Delete this custom gem", key=f"delete_{gem.get('id')}"):
                    remaining = [item for item in custom_gems if item.get("id") != gem.get("id")]
                    write_json(CUSTOM_GEMS_PATH, remaining)
                    st.success("Deleted. Refresh the page to update dropdown.")

with tabs[3]:
    st.header("Image Tools")
    tool_card(
        "Fooocus",
        "Story scene image generation. This is a separate Image Lab notebook/runtime, not installed in app.py.",
        "separate_lab_planned",
        IMAGE_OUTPUT_DIR,
        {"Story/scene text": "", "Image prompt": "", "Style notes": "", "Output folder": str(IMAGE_OUTPUT_DIR)},
        IMAGE_JOB_DIR,
    )

with tabs[4]:
    st.header("Voice Tools")
    tool_card(
        "XTTS v2",
        "Text-to-speech / voice cloning. This is a separate Voice Lab notebook/runtime, not installed in app.py.",
        "separate_lab_planned",
        VOICE_OUTPUT_DIR,
        {"Text/script path or text": "", "Reference voice file path": "", "Language": "bn", "Output folder": str(VOICE_OUTPUT_DIR)},
        VOICE_JOB_DIR,
        "Use only your own voice, licensed voice, or voice with clear permission.",
    )

with tabs[5]:
    st.header("Video Tools")
    face_col, live_col = st.columns(2)
    with face_col:
        tool_card(
            "FaceFusion",
            "Face swap / face enhancement / face-related video workflow. Install and test in a separate FaceFusion Lab notebook.",
            "separate_lab_install_now",
            FACEFUSION_OUTPUT_DIR,
            {"Source face image path": "", "Target image/video path": "", "Output folder": str(FACEFUSION_OUTPUT_DIR)},
            VIDEO_JOB_DIR,
            "Use only your own face, licensed assets, or people who gave clear permission. Do not impersonate real people or create misleading content.",
        )
    with live_col:
        tool_card(
            "LivePortrait",
            "Animate a static portrait image using a driving video or motion reference. Install and test in a separate LivePortrait Lab notebook.",
            "separate_lab_install_now",
            LIVEPORTRAIT_OUTPUT_DIR,
            {"Source portrait image path": "", "Driving video path": "", "Output folder": str(LIVEPORTRAIT_OUTPUT_DIR)},
            VIDEO_JOB_DIR,
            "Use only your own face, licensed assets, or people who gave clear permission. Do not impersonate real people or create misleading content.",
        )

with tabs[6]:
    st.header("Output Library")
    files = sorted(OUTPUT_DIR.glob("*.txt"), key=lambda item: item.stat().st_mtime, reverse=True)[:10]
    if not files:
        st.info("No saved text outputs yet.")
    else:
        selected = st.selectbox("Select output", [str(file) for file in files])
        st.code(selected)
        st.text_area("Preview", Path(selected).read_text(encoding="utf-8"), height=360)

with tabs[7]:
    st.header("Settings")
    st.write("Ollama endpoint:", OLLAMA_ENDPOINT)
    st.write("Ollama health endpoint:", OLLAMA_HEALTH_ENDPOINT)
    st.write("Base directory:", BASE_DIR)
    st.write("Output directory:", OUTPUT_DIR)
    st.write("Config directory:", CONFIG_DIR)
    st.write("Custom gems path:", CUSTOM_GEMS_PATH)
    st.write("Tool links path:", TOOL_LINKS_PATH)
    st.write("Text jobs path:", TEXT_JOB_DIR)
    st.write("Image jobs path:", IMAGE_JOB_DIR)
    st.write("Voice jobs path:", VOICE_JOB_DIR)
    st.write("Video jobs path:", VIDEO_JOB_DIR)
    st.write("Image outputs path:", IMAGE_OUTPUT_DIR)
    st.write("Voice outputs path:", VOICE_OUTPUT_DIR)
    st.write("FaceFusion outputs path:", FACEFUSION_OUTPUT_DIR)
    st.write("LivePortrait outputs path:", LIVEPORTRAIT_OUTPUT_DIR)
    st.write("Current model:", model)
    if st.button("Check Ollama Health"):
        try:
            health = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=30)
            health.raise_for_status()
            st.json(health.json())
        except Exception as exc:
            st.error(f"Ollama health check failed: {exc}")
