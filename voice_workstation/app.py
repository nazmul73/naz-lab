"""Naz Lab Voice Workstation Phase 4.1.

Polished voice preset builder for True Noir Tales, ToolFlow, and General workflows.
Creates narration prompts, TTS direction, and copy-ready voice packages.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, OUTPUT_LOG_JSON, WORKSTATION_LINKS_JSON  # noqa: E402
from shared.json_utils import append_output_log, update_workstation_status  # noqa: E402

PHASE = "4.1"
VOICE_OUTPUTS = BASE_PATH / "voice_outputs"
VOICE_DIRECTIONS = BASE_PATH / "voice_directions"

PROJECT_PRESETS = ["True Noir Tales", "ToolFlow", "General"]
CONTENT_TYPES = ["Reel voiceover", "Story narration", "General Facebook narration", "Carousel voice script", "Short ad/explainer"]
LANGUAGE_OPTIONS = ["English", "Bangla", "Mixed English-Bangla"]
REGIONAL_TONES = ["Neutral", "Rangpur/Nilphamari", "Dhaka", "Chattogram", "Sylhet", "Noakhali/Comilla"]
VOICE_TONES = ["dark calm", "suspenseful", "investigative", "serious", "reflective", "practical", "modern", "clean", "confident", "friendly professional", "natural conversational"]
PACING_OPTIONS = ["slow", "medium-slow", "medium", "medium-fast", "fast but clear"]
ENERGY_OPTIONS = ["low controlled", "balanced", "medium dramatic", "lightly upbeat", "high but not hype"]
ACCENT_OPTIONS = ["neutral international English", "light South Asian English", "natural Bangla", "Rangpur/Nilphamari Bangla flavor"]
SCRIPT_LENGTHS = ["15 seconds", "30 seconds", "45 seconds", "60 seconds", "Custom"]
SCRIPT_STRUCTURES = ["Hook-Body-CTA", "Hook-Problem-Solution-CTA", "Story-Context-Tension-Question", "Listicle", "Tutorial steps", "Narration only"]
DELIVERY_STYLES = ["clean spoken", "documentary", "dramatic restrained", "creator explainer", "conversational", "premium ad voice"]
PAUSE_STYLES = ["minimal pauses", "short dramatic pauses", "clear sentence breaks", "fast flow", "slow tension"]

PROJECT_DEFAULTS = {
    "True Noir Tales": {
        "language": "English",
        "tone": "dark calm",
        "pacing": "medium-slow",
        "energy": "low controlled",
        "accent": "neutral international English",
        "structure": "Story-Context-Tension-Question",
        "delivery": "dramatic restrained",
        "pause": "short dramatic pauses",
        "style": "English true crime narration, suspenseful but not overacted, documentary storytelling cadence, emotional control, short dramatic pauses.",
    },
    "ToolFlow": {
        "language": "English",
        "tone": "practical",
        "pacing": "medium",
        "energy": "balanced",
        "accent": "neutral international English",
        "structure": "Hook-Problem-Solution-CTA",
        "delivery": "creator explainer",
        "pause": "clear sentence breaks",
        "style": "English productivity explainer narration, clean and useful, confident but non-hype, modern creator/instructor feel.",
    },
    "General": {
        "language": "Bangla",
        "tone": "natural conversational",
        "pacing": "medium",
        "energy": "balanced",
        "accent": "natural Bangla",
        "structure": "Hook-Body-CTA",
        "delivery": "clean spoken",
        "pause": "clear sentence breaks",
        "style": "Natural ready-to-use narration. Bangla should sound human, simple, and spoken, with Rangpur/Nilphamari flavor when requested.",
    },
}

CONTENT_RULES = {
    "Reel voiceover": "Start with a strong first line. Keep sentences short. Make it easy to record in one take.",
    "Story narration": "Use a clear story flow. Build emotion slowly. Keep the narration human and grounded.",
    "General Facebook narration": "Make it natural, direct, and suitable for a Facebook audience.",
    "Carousel voice script": "Make it slide-friendly. Each sentence should work as a spoken caption for one idea.",
    "Short ad/explainer": "Make it concise, practical, benefit-led, and non-hype.",
}


def ensure_dirs() -> None:
    VOICE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    VOICE_DIRECTIONS.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "voice"


def build_voice_direction(
    project: str,
    content_type: str,
    language: str,
    regional_tone: str,
    voice_tone: str,
    pacing: str,
    energy: str,
    accent: str,
    length: str,
    structure: str,
    delivery_style: str,
    pause_style: str,
    input_text: str,
    custom_note: str,
) -> str:
    project_style = PROJECT_DEFAULTS.get(project, PROJECT_DEFAULTS["General"])["style"]
    parts = [
        f"Project preset: {project}",
        f"Content type: {content_type}",
        f"Language: {language}",
        f"Regional tone: {regional_tone}",
        f"Voice tone: {voice_tone}",
        f"Pacing: {pacing}",
        f"Energy: {energy}",
        f"Accent/style: {accent}",
        f"Target length: {length}",
        f"Script structure: {structure}",
        f"Delivery style: {delivery_style}",
        f"Pause style: {pause_style}",
        f"Project style: {project_style}",
        f"Content rule: {CONTENT_RULES.get(content_type, '')}",
        "Delivery rules: sound natural, clear, and human; avoid robotic phrasing; use short spoken sentences; add pauses only where useful.",
    ]
    if project == "True Noir Tales":
        parts.append("True Noir Tales rules: English by default, suspenseful but controlled, adult-focused storytelling, no gore description, no sensational overacting, end with curiosity or a question when useful.")
    if project == "ToolFlow":
        parts.append("ToolFlow rules: English by default, practical explainer voice, useful and premium, no fake income claims, no spammy hype, make the value clear quickly.")
    if language == "Bangla":
        parts.append("Bangla rules: natural spoken Bangla, simple sentence flow, netizen-friendly when needed, not stiff textbook Bangla.")
    if regional_tone == "Rangpur/Nilphamari":
        parts.append("Rangpur/Nilphamari rule: use light North Bengal flavor only when Bangla or mixed language is selected; do not overdo dialect.")
    if custom_note.strip():
        parts.append(f"Custom direction: {custom_note.strip()}")
    if input_text.strip():
        parts.append(f"Source text/topic:\n{input_text.strip()}")
    return "\n\n".join(parts)


def build_tts_direction(
    project: str,
    language: str,
    voice_tone: str,
    pacing: str,
    energy: str,
    accent: str,
    delivery_style: str,
    pause_style: str,
) -> str:
    return "\n".join(
        [
            f"TTS project: {project}",
            f"Voice language: {language}",
            f"Tone: {voice_tone}",
            f"Pacing: {pacing}",
            f"Energy: {energy}",
            f"Accent/style: {accent}",
            f"Delivery style: {delivery_style}",
            f"Pause style: {pause_style}",
            "Avoid robotic delivery. Keep pronunciation clear. Do not overact. Keep breaths and pauses natural.",
        ]
    )


def build_voice_script(project: str, content_type: str, language: str, structure: str, input_text: str) -> str:
    if not input_text.strip():
        return ""
    source = input_text.strip()
    if project == "True Noir Tales":
        if structure == "Story-Context-Tension-Question":
            return (
                "Hook:\n"
                "What looked normal at first was hiding something much darker.\n\n"
                "Context:\n"
                f"{source}\n\n"
                "Tension:\n"
                "The detail that matters is not the loudest one. It is the one people almost missed.\n\n"
                "Question CTA:\n"
                "What would you have noticed first?"
            )
        return f"Hook:\nWhat looked normal was not normal at all.\n\nVoiceover:\n{source}\n\nCTA:\nWhat would you have noticed first?"
    if project == "ToolFlow":
        if structure == "Hook-Problem-Solution-CTA":
            return (
                "Hook:\n"
                "Most people use AI tools randomly. The real advantage comes from using them as a system.\n\n"
                "Problem:\n"
                "Random tools create random results.\n\n"
                "Solution:\n"
                f"{source}\n\n"
                "CTA:\n"
                "Would you use this workflow?"
            )
        return f"Hook:\nHere is a cleaner way to use AI.\n\nVoiceover:\n{source}\n\nCTA:\nWould you try this?"
    if language == "Bangla":
        return (
            "Hook:\n"
            "এই কথাটা অনেকেই খেয়াল করে না।\n\n"
            "Voiceover:\n"
            f"{source}\n\n"
            "CTA:\n"
            "তোমার কী মনে হয়?"
        )
    return f"Hook:\nHere is the simple version.\n\nVoiceover:\n{source}\n\nCTA:\nWhat do you think?"


def save_voice_file(project: str, content: str, prefix: str) -> Path:
    ensure_dirs()
    path = VOICE_OUTPUTS / f"{prefix}_{safe_name(project)}_{now_stamp()}.txt"
    path.write_text(content, encoding="utf-8")
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="voice_workstation",
        event="voice_file_saved",
        details={"path": str(path), "project": project, "prefix": prefix},
    )
    return path


def render_builder() -> None:
    st.header("Voice package builder")
    project = st.selectbox("Project preset", PROJECT_PRESETS)
    defaults = PROJECT_DEFAULTS[project]

    content_type = st.selectbox("Content type", CONTENT_TYPES)
    language = st.selectbox("Language", LANGUAGE_OPTIONS, index=LANGUAGE_OPTIONS.index(defaults["language"]))
    regional_tone = st.selectbox("Regional tone", REGIONAL_TONES)
    voice_tone = st.selectbox("Voice tone", VOICE_TONES, index=VOICE_TONES.index(defaults["tone"]))
    pacing = st.selectbox("Pacing", PACING_OPTIONS, index=PACING_OPTIONS.index(defaults["pacing"]))
    energy = st.selectbox("Energy", ENERGY_OPTIONS, index=ENERGY_OPTIONS.index(defaults["energy"]))
    accent = st.selectbox("Accent/style", ACCENT_OPTIONS, index=ACCENT_OPTIONS.index(defaults["accent"]))
    length = st.selectbox("Target length", SCRIPT_LENGTHS, index=1)
    structure = st.selectbox("Script structure", SCRIPT_STRUCTURES, index=SCRIPT_STRUCTURES.index(defaults["structure"]))
    delivery_style = st.selectbox("Delivery style", DELIVERY_STYLES, index=DELIVERY_STYLES.index(defaults["delivery"]))
    pause_style = st.selectbox("Pause style", PAUSE_STYLES, index=PAUSE_STYLES.index(defaults["pause"]))

    input_text = st.text_area("Source topic/script", height=180, placeholder="Paste a topic, draft script, or narration idea here.")
    custom_note = st.text_area("Custom voice direction", height=100, placeholder="Example: Make it more suspenseful, softer, faster, more conversational, etc.")

    direction = build_voice_direction(project, content_type, language, regional_tone, voice_tone, pacing, energy, accent, length, structure, delivery_style, pause_style, input_text, custom_note)
    tts_direction = build_tts_direction(project, language, voice_tone, pacing, energy, accent, delivery_style, pause_style)
    script = build_voice_script(project, content_type, language, structure, input_text)
    combined = f"VOICE DIRECTION:\n{direction}\n\nTTS DIRECTION:\n{tts_direction}\n\nSCRIPT DRAFT:\n{script}" if script else f"VOICE DIRECTION:\n{direction}\n\nTTS DIRECTION:\n{tts_direction}"

    st.markdown("### Narration direction")
    st.text_area("Copy-ready narration direction", direction, height=260)

    st.markdown("### TTS direction")
    st.text_area("Copy-ready TTS direction", tts_direction, height=160)

    st.markdown("### Script draft")
    st.text_area("Script draft", script, height=220)

    st.markdown("### Combined voice package")
    st.text_area("Copy-ready combined package", combined, height=340)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Save narration direction"):
            path = save_voice_file(project, direction, "voice_direction")
            st.success(f"Saved: {path}")
    with col2:
        if st.button("Save TTS direction"):
            path = save_voice_file(project, tts_direction, "tts_direction")
            st.success(f"Saved: {path}")
    with col3:
        if st.button("Save combined package"):
            path = save_voice_file(project, combined, "voice_package")
            st.success(f"Saved: {path}")


def render_library() -> None:
    st.header("Voice output library")
    ensure_dirs()
    files = sorted([path for path in VOICE_OUTPUTS.glob("*.txt") if path.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)
    if not files:
        st.info("No voice files saved yet.")
        return
    selected = st.selectbox("Select voice file", [path.name for path in files])
    path = VOICE_OUTPUTS / selected
    st.caption(str(path))
    st.text_area("Preview", path.read_text(encoding="utf-8", errors="ignore"), height=420)


def render_status() -> None:
    st.header("Status")
    ensure_dirs()
    files = list(VOICE_OUTPUTS.glob("*.txt"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Phase", PHASE)
    c2.metric("Voice files", len(files))
    c3.metric("TTS backend", "future")

    st.markdown("### Voice project defaults")
    st.json(PROJECT_DEFAULTS)

    st.markdown("### Content rules")
    st.json(CONTENT_RULES)

    st.markdown("### Paths")
    st.write({
        "voice_outputs": str(VOICE_OUTPUTS),
        "voice_directions": str(VOICE_DIRECTIONS),
        "workstation_links_json": str(WORKSTATION_LINKS_JSON),
    })


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("Phase 4.1 creates narration direction, TTS direction, and voice packages. It does not run TTS yet.")
    st.markdown("Future build: TTS backend integration and audio output library.")
    st.code("streamlit run voice_workstation/app.py --server.port 8504 --server.address 0.0.0.0", language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Voice Workstation", page_icon="🎙️", layout="wide")
    st.title("🎙️ Naz Lab Voice Workstation")
    st.caption("Phase 4.1 — polished presets, narration direction, TTS direction, voice package builder.")
    st.info("True Noir Tales and ToolFlow are English-first voice projects. Bangla and Rangpur/Nilphamari support are included.")

    ensure_dirs()
    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "voice_workstation",
        {"status": "running", "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")},
    )

    tabs = st.tabs(["Status", "Builder", "Library", "Launch"])
    with tabs[0]:
        render_status()
    with tabs[1]:
        render_builder()
    with tabs[2]:
        render_library()
    with tabs[3]:
        render_launch()


if __name__ == "__main__":
    main()
