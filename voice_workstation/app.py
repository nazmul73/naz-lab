"""Naz Lab Voice Workstation Phase 4.5 safer reference manager.

Stable Voice Workstation with narration direction, TTS direction,
voice packages, future audio metadata, and safer authorized reference voice workflow planning.
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, OUTPUT_LOG_JSON, WORKSTATION_LINKS_JSON  # noqa: E402
from shared.json_utils import append_output_log, safe_read_json, safe_write_json, update_workstation_status  # noqa: E402
from shared.reference_asset_policy import (  # noqa: E402
    REFERENCE_ALLOWED_USE,
    REFERENCE_ASSET_POLICY,
    REFERENCE_DISALLOWED_USE,
    REFERENCE_MANAGER_UI_REQUIREMENTS,
    VOICE_REFERENCE_ALLOWED_EXTENSIONS,
    VOICE_REFERENCE_POLICY_FIELDS,
    is_allowed_reference_extension,
)

PHASE = "4.5"
PHASE_STATUS = "clone-ready-safe-reference-manager"
VOICE_OUTPUTS = BASE_PATH / "voice_outputs"
VOICE_DIRECTIONS = BASE_PATH / "voice_directions"
AUDIO_OUTPUTS = BASE_PATH / "audio_outputs"
VOICE_PACKAGES = BASE_PATH / "voice_packages"
VOICE_REFERENCES = BASE_PATH / "voice_references"
VOICE_CLONE_PACKAGES = BASE_PATH / "voice_clone_packages"

PROJECT_PRESETS = ["True Noir Tales", "ToolFlow", "General"]
CONTENT_TYPES = ["Reel voiceover", "Story narration", "General Facebook narration", "Carousel voice script", "Short ad/explainer"]
LANGUAGE_OPTIONS = ["English", "Bangla", "Mixed English-Bangla"]
REGIONAL_TONES = ["Neutral", "Rangpur/Nilphamari", "Dhaka", "Chattogram", "Sylhet", "Noakhali/Comilla"]
VOICE_MODES = ["Original / generic voice direction", "Authorized reference voice clone planning", "Brand voice profile"]
VOICE_TONES = ["dark calm", "suspenseful", "investigative", "serious", "reflective", "practical", "modern", "clean", "confident", "friendly professional", "natural conversational"]
PACING_OPTIONS = ["slow", "medium-slow", "medium", "medium-fast", "fast but clear"]
ENERGY_OPTIONS = ["low controlled", "balanced", "medium dramatic", "lightly upbeat", "high but not hype"]
ACCENT_OPTIONS = ["neutral international English", "light South Asian English", "natural Bangla", "Rangpur/Nilphamari Bangla flavor"]
SCRIPT_LENGTHS = ["15 seconds", "30 seconds", "45 seconds", "60 seconds", "Custom"]
SCRIPT_STRUCTURES = ["Hook-Body-CTA", "Hook-Problem-Solution-CTA", "Story-Context-Tension-Question", "Listicle", "Tutorial steps", "Narration only"]
DELIVERY_STYLES = ["clean spoken", "documentary", "dramatic restrained", "creator explainer", "conversational", "premium ad voice"]
PAUSE_STYLES = ["minimal pauses", "short dramatic pauses", "clear sentence breaks", "fast flow", "slow tension"]
PACKAGE_STATUS = ["draft", "ready_for_tts", "ready_for_voice_clone", "audio_generated", "blocked", "archived"]
AUDIO_EXTENSIONS = set(VOICE_REFERENCE_ALLOWED_EXTENSIONS)

CLONE_SAFETY_RULES = {
    "Policy": REFERENCE_ASSET_POLICY,
    "Authorization": "Only use voice cloning with a user-provided or explicitly authorized reference voice.",
    "No impersonation": "Do not clone celebrities, public figures, or another person's voice without permission.",
    "No deception": "Do not use cloned voice for deceptive, fraudulent, or misleading content.",
    "Reference quality": "Use clean reference audio with minimal noise, natural speech, and enough duration for a future backend.",
    "Labeling": "Keep metadata that this is a reference-voice workflow.",
}

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
    AUDIO_OUTPUTS.mkdir(parents=True, exist_ok=True)
    VOICE_PACKAGES.mkdir(parents=True, exist_ok=True)
    VOICE_REFERENCES.mkdir(parents=True, exist_ok=True)
    VOICE_CLONE_PACKAGES.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "voice"


def suggested_audio_filename(project: str, content_type: str) -> str:
    return f"{safe_name(project)}_{safe_name(content_type)}_{now_stamp()}.mp3"


def list_files(folder: Path, suffixes: set[str] | None = None) -> list[Path]:
    if not folder.exists():
        return []
    files = [path for path in folder.glob("*") if path.is_file()]
    if suffixes:
        files = [path for path in files if path.suffix.lower() in suffixes]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)


def validate_audio_path(path_text: str) -> tuple[bool, str]:
    if not path_text.strip():
        return False, "No audio path provided yet."
    path = Path(path_text.strip())
    if not path.exists():
        return False, "Audio path does not exist yet. Generate or save the audio file first."
    if not is_allowed_reference_extension(path.name, "voice"):
        return False, "Audio path exists but file extension is not supported."
    return True, "Audio path exists and looks valid."


def validate_reference_path(path_text: str) -> tuple[bool, str]:
    if not path_text.strip():
        return False, "No reference voice path provided yet."
    path = Path(path_text.strip())
    if not path.exists():
        return False, "Reference voice file does not exist yet. Upload or save authorized reference audio first."
    if not is_allowed_reference_extension(path.name, "voice"):
        return False, "Reference path exists but file extension is not supported."
    return True, "Reference voice file exists and looks valid."


def save_uploaded_reference(uploaded_file: Any) -> Path | None:
    if uploaded_file is None:
        return None
    if not is_allowed_reference_extension(uploaded_file.name, "voice"):
        st.error("Unsupported reference audio type. Allowed: " + ", ".join(VOICE_REFERENCE_ALLOWED_EXTENSIONS))
        return None
    ensure_dirs()
    destination = VOICE_REFERENCES / f"reference_voice_{now_stamp()}_{safe_name(Path(uploaded_file.name).stem)}{Path(uploaded_file.name).suffix.lower()}"
    with destination.open("wb") as output_file:
        shutil.copyfileobj(uploaded_file, output_file)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="voice_workstation",
        event="reference_voice_uploaded",
        details={"path": str(destination), "policy": REFERENCE_ASSET_POLICY},
    )
    return destination


def resolve_reference_path(uploaded_path: Path | None, selected_reference: str, manual_reference_path: str) -> str:
    if uploaded_path:
        return str(uploaded_path)
    if selected_reference and selected_reference != "No saved reference selected":
        return str(VOICE_REFERENCES / selected_reference)
    return manual_reference_path.strip()


def build_reference_metadata(reference_voice_path: str, authorized: bool, notes: str, intended_use: str) -> dict[str, Any]:
    metadata = dict(VOICE_REFERENCE_POLICY_FIELDS)
    metadata.update(
        {
            "reference_voice_path": reference_voice_path,
            "reference_voice_authorized": authorized,
            "reference_voice_notes": notes.strip(),
            "reference_intended_use": intended_use.strip(),
            "reference_policy": REFERENCE_ASSET_POLICY,
            "reference_allowed_extensions": VOICE_REFERENCE_ALLOWED_EXTENSIONS,
            "reference_policy_phase": "11.0",
        }
    )
    return metadata


def reference_ready_for_clone(voice_mode: str, reference_voice_path: str, authorized: bool) -> tuple[bool, str]:
    if voice_mode != "Authorized reference voice clone planning":
        return True, "Reference voice is not required for this voice mode."
    ref_ok, ref_message = validate_reference_path(reference_voice_path)
    if not ref_ok:
        return False, ref_message
    if not authorized:
        return False, "Authorization is required before saving a reference voice clone package."
    return True, "Reference voice is valid and authorization is confirmed."


def render_reference_manager(voice_mode: str) -> tuple[str, bool, str, dict[str, Any], bool, str]:
    st.markdown("### Safer reference voice manager")
    st.warning("Reference voice must be user-provided or explicitly authorized. Do not use unauthorized or deceptive voice references.")
    st.caption(f"Reference folder: {VOICE_REFERENCES}")

    with st.expander("Reference Asset Policy", expanded=False):
        st.write(REFERENCE_ASSET_POLICY)
        st.markdown("Allowed use")
        st.json(REFERENCE_ALLOWED_USE)
        st.markdown("Disallowed use")
        st.json(REFERENCE_DISALLOWED_USE)
        st.markdown("Reference manager UI requirements")
        st.json(REFERENCE_MANAGER_UI_REQUIREMENTS)

    uploaded_file = st.file_uploader("Upload authorized reference audio", type=[ext.lstrip(".") for ext in VOICE_REFERENCE_ALLOWED_EXTENSIONS])
    uploaded_path = save_uploaded_reference(uploaded_file) if uploaded_file is not None else None
    if uploaded_path:
        st.success(f"Uploaded reference saved: {uploaded_path}")

    saved_references = list_files(VOICE_REFERENCES, AUDIO_EXTENSIONS)
    reference_options = ["No saved reference selected"] + [path.name for path in saved_references]
    selected_reference = st.selectbox("Saved reference list", reference_options)
    manual_reference_path = st.text_input("Selected/manual reference voice path", value="")
    reference_voice_path = resolve_reference_path(uploaded_path, selected_reference, manual_reference_path)
    if reference_voice_path:
        st.caption(reference_voice_path)

    clone_authorized = st.checkbox(
        "I confirm this reference voice is user-provided or explicitly authorized for this workflow.",
        value=False,
    )
    clone_notes = st.text_area(
        "Reference voice notes / intended use",
        height=90,
        placeholder="Example: This is my own voice. Use it only for Bangla narration planning.",
    )

    reference_metadata = build_reference_metadata(
        reference_voice_path=reference_voice_path,
        authorized=clone_authorized,
        notes=clone_notes,
        intended_use="voice clone planning" if voice_mode == "Authorized reference voice clone planning" else "voice direction planning",
    )
    ref_ready, ref_message = reference_ready_for_clone(voice_mode, reference_voice_path, clone_authorized)
    if voice_mode == "Authorized reference voice clone planning":
        if ref_ready:
            st.success(ref_message)
        else:
            st.error(ref_message)
    elif reference_voice_path and not clone_authorized:
        st.info("Reference path is recorded as non-authorized metadata only; generic/brand planning can continue without using it for cloning.")

    with st.expander("Reference package metadata preview", expanded=False):
        st.json(reference_metadata)
    return reference_voice_path, clone_authorized, clone_notes, reference_metadata, ref_ready, ref_message


def build_clone_direction(voice_mode: str, reference_voice_path: str, clone_authorized: bool, clone_notes: str) -> str:
    if voice_mode != "Authorized reference voice clone planning":
        return "Voice cloning: not selected. Use original/generic or brand voice direction."
    parts = [
        "Voice cloning mode: authorized reference voice clone planning.",
        f"Reference voice path: {reference_voice_path or '[not provided]'}",
        f"Authorization confirmed: {clone_authorized}",
        f"Reference policy: {REFERENCE_ASSET_POLICY}",
        "Clone safety: use only user-provided or explicitly authorized voice references; no celebrity/public figure impersonation; no deceptive use.",
        "Future backend note: this package only prepares metadata and direction. It does not clone or generate a voice yet.",
    ]
    if clone_notes.strip():
        parts.append(f"Reference notes: {clone_notes.strip()}")
    return "\n".join(parts)


def build_voice_direction(project: str, content_type: str, language: str, regional_tone: str, voice_mode: str, voice_tone: str, pacing: str, energy: str, accent: str, length: str, structure: str, delivery_style: str, pause_style: str, input_text: str, custom_note: str, clone_direction: str) -> str:
    project_style = PROJECT_DEFAULTS.get(project, PROJECT_DEFAULTS["General"])["style"]
    parts = [
        f"Project preset: {project}",
        f"Content type: {content_type}",
        f"Language: {language}",
        f"Regional tone: {regional_tone}",
        f"Voice mode: {voice_mode}",
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
        clone_direction,
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


def build_tts_direction(project: str, language: str, voice_mode: str, voice_tone: str, pacing: str, energy: str, accent: str, delivery_style: str, pause_style: str) -> str:
    return "\n".join([
        f"TTS project: {project}",
        f"Voice language: {language}",
        f"Voice mode: {voice_mode}",
        f"Tone: {voice_tone}",
        f"Pacing: {pacing}",
        f"Energy: {energy}",
        f"Accent/style: {accent}",
        f"Delivery style: {delivery_style}",
        f"Pause style: {pause_style}",
        "Avoid robotic delivery. Keep pronunciation clear. Do not overact. Keep breaths and pauses natural.",
    ])


def build_voice_script(project: str, content_type: str, language: str, structure: str, input_text: str) -> str:
    if not input_text.strip():
        return ""
    source = input_text.strip()
    if project == "True Noir Tales":
        if structure == "Story-Context-Tension-Question":
            return "Hook:\nWhat looked normal at first was hiding something much darker.\n\nContext:\n" + source + "\n\nTension:\nThe detail that matters is not the loudest one. It is the one people almost missed.\n\nQuestion CTA:\nWhat would you have noticed first?"
        return "Hook:\nWhat looked normal was not normal at all.\n\nVoiceover:\n" + source + "\n\nCTA:\nWhat would you have noticed first?"
    if project == "ToolFlow":
        if structure == "Hook-Problem-Solution-CTA":
            return "Hook:\nMost people use AI tools randomly. The real advantage comes from using them as a system.\n\nProblem:\nRandom tools create random results.\n\nSolution:\n" + source + "\n\nCTA:\nWould you use this workflow?"
        return "Hook:\nHere is a cleaner way to use AI.\n\nVoiceover:\n" + source + "\n\nCTA:\nWould you try this?"
    if language == "Bangla":
        return "Hook:\nএই কথাটা অনেকেই খেয়াল করে না।\n\nVoiceover:\n" + source + "\n\nCTA:\nতোমার কী মনে হয়?"
    return "Hook:\nHere is the simple version.\n\nVoiceover:\n" + source + "\n\nCTA:\nWhat do you think?"


def build_package_json(project: str, content_type: str, language: str, regional_tone: str, status: str, suggested_audio_path: str, audio_output_path: str, direction: str, tts_direction: str, script: str, combined: str, voice_mode: str, reference_voice_path: str, clone_authorized: bool, clone_direction: str, reference_metadata: dict[str, Any]) -> dict[str, Any]:
    package = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "phase": PHASE,
        "project_preset": project,
        "content_type": content_type,
        "language": language,
        "regional_tone": regional_tone,
        "voice_mode": voice_mode,
        "reference_voice_path": reference_voice_path,
        "clone_authorized": clone_authorized,
        "reference_voice_authorized": clone_authorized,
        "clone_direction": clone_direction,
        "status": status,
        "suggested_audio_path": suggested_audio_path,
        "audio_output_path": audio_output_path,
        "narration_direction": direction,
        "tts_direction": tts_direction,
        "script_draft": script,
        "combined_package": combined,
        "future_clone_backend": "placeholder",
    }
    package.update(reference_metadata)
    return package


def save_text_file(project: str, content: str, prefix: str) -> Path:
    ensure_dirs()
    path = VOICE_OUTPUTS / f"{prefix}_{safe_name(project)}_{now_stamp()}.txt"
    path.write_text(content, encoding="utf-8")
    append_output_log(OUTPUT_LOG_JSON, workstation="voice_workstation", event="voice_file_saved", details={"path": str(path), "project": project, "prefix": prefix})
    return path


def save_package_json(package: dict[str, Any]) -> Path:
    ensure_dirs()
    folder = VOICE_CLONE_PACKAGES if package.get("voice_mode") == "Authorized reference voice clone planning" else VOICE_PACKAGES
    path = folder / f"voice_package_{safe_name(package['project_preset'])}_{now_stamp()}.json"
    safe_write_json(path, package)
    append_output_log(OUTPUT_LOG_JSON, workstation="voice_workstation", event="voice_package_saved", details={"path": str(path), "project": package["project_preset"], "status": package["status"], "voice_mode": package.get("voice_mode", ""), "reference_voice_authorized": package.get("reference_voice_authorized", False)})
    return path


def render_builder() -> None:
    st.header("Voice package builder")
    project = st.selectbox("Project preset", PROJECT_PRESETS)
    defaults = PROJECT_DEFAULTS[project]
    content_type = st.selectbox("Content type", CONTENT_TYPES)
    language = st.selectbox("Language", LANGUAGE_OPTIONS, index=LANGUAGE_OPTIONS.index(defaults["language"]))
    regional_tone = st.selectbox("Regional tone", REGIONAL_TONES)
    voice_mode = st.selectbox("Voice mode", VOICE_MODES)
    voice_tone = st.selectbox("Voice tone", VOICE_TONES, index=VOICE_TONES.index(defaults["tone"]))
    pacing = st.selectbox("Pacing", PACING_OPTIONS, index=PACING_OPTIONS.index(defaults["pacing"]))
    energy = st.selectbox("Energy", ENERGY_OPTIONS, index=ENERGY_OPTIONS.index(defaults["energy"]))
    accent = st.selectbox("Accent/style", ACCENT_OPTIONS, index=ACCENT_OPTIONS.index(defaults["accent"]))
    length = st.selectbox("Target length", SCRIPT_LENGTHS, index=1)
    structure = st.selectbox("Script structure", SCRIPT_STRUCTURES, index=SCRIPT_STRUCTURES.index(defaults["structure"]))
    delivery_style = st.selectbox("Delivery style", DELIVERY_STYLES, index=DELIVERY_STYLES.index(defaults["delivery"]))
    pause_style = st.selectbox("Pause style", PAUSE_STYLES, index=PAUSE_STYLES.index(defaults["pause"]))
    package_status = st.selectbox("Voice package status", PACKAGE_STATUS)

    suggested_audio = AUDIO_OUTPUTS / suggested_audio_filename(project, content_type)
    audio_output_path = st.text_input("Future audio output path", value=str(suggested_audio))
    audio_ok, audio_message = validate_audio_path(audio_output_path)
    if audio_ok:
        st.success(audio_message)
    else:
        st.warning(audio_message)

    reference_voice_path, clone_authorized, clone_notes, reference_metadata, ref_ready, ref_message = render_reference_manager(voice_mode)

    input_text = st.text_area("Source topic/script", height=180, placeholder="Paste a topic, draft script, or narration idea here.")
    custom_note = st.text_area("Custom voice direction", height=100, placeholder="Example: Make it more suspenseful, softer, faster, more conversational, etc.")

    clone_direction = build_clone_direction(voice_mode, reference_voice_path, clone_authorized, clone_notes)
    direction = build_voice_direction(project, content_type, language, regional_tone, voice_mode, voice_tone, pacing, energy, accent, length, structure, delivery_style, pause_style, input_text, custom_note, clone_direction)
    tts_direction = build_tts_direction(project, language, voice_mode, voice_tone, pacing, energy, accent, delivery_style, pause_style)
    script = build_voice_script(project, content_type, language, structure, input_text)
    combined = f"VOICE DIRECTION:\n{direction}\n\nTTS DIRECTION:\n{tts_direction}\n\nSCRIPT DRAFT:\n{script}" if script else f"VOICE DIRECTION:\n{direction}\n\nTTS DIRECTION:\n{tts_direction}"
    package_json = build_package_json(project, content_type, language, regional_tone, package_status, str(suggested_audio), audio_output_path, direction, tts_direction, script, combined, voice_mode, reference_voice_path, clone_authorized, clone_direction, reference_metadata)

    st.markdown("### Stable workflow")
    st.markdown("1. Pick project and content type.  \n2. Choose original, brand voice, or authorized reference clone planning.  \n3. Upload/select only authorized reference audio if clone planning is selected.  \n4. Paste topic/script.  \n5. Save package JSON.  \n6. Later, connect a TTS or authorized voice-clone backend.")

    st.text_area("Copy-ready clone direction", clone_direction, height=150)
    st.text_area("Copy-ready narration direction", direction, height=260)
    st.text_area("Copy-ready TTS direction", tts_direction, height=150)
    st.text_area("Script draft", script, height=200)
    st.text_area("Copy-ready combined package", combined, height=320)

    with st.expander("Voice package JSON preview", expanded=False):
        st.json(package_json)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Save narration"):
            st.success(f"Saved: {save_text_file(project, direction, 'voice_direction')}")
    with col2:
        if st.button("Save TTS"):
            st.success(f"Saved: {save_text_file(project, tts_direction, 'tts_direction')}")
    with col3:
        if st.button("Save combined"):
            st.success(f"Saved: {save_text_file(project, combined, 'voice_package')}")
    with col4:
        if st.button("Save package JSON"):
            if voice_mode == "Authorized reference voice clone planning" and not ref_ready:
                st.error(f"Cannot save clone package: {ref_message}")
            else:
                st.success(f"Saved: {save_package_json(package_json)}")


def render_library() -> None:
    st.header("Voice output library")
    ensure_dirs()
    files = sorted([path for path in VOICE_OUTPUTS.glob("*.txt") if path.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)
    packages = sorted([path for path in VOICE_PACKAGES.glob("*.json") if path.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)
    clone_packages = sorted([path for path in VOICE_CLONE_PACKAGES.glob("*.json") if path.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)
    references = list_files(VOICE_REFERENCES, AUDIO_EXTENSIONS)
    st.metric("Text voice files", len(files))
    st.metric("Package JSON files", len(packages))
    st.metric("Clone package JSON files", len(clone_packages))
    st.metric("Reference voice files", len(references))
    if references:
        st.markdown("### Saved reference voices")
        selected_reference = st.selectbox("Select reference voice", [path.name for path in references])
        ref_path = VOICE_REFERENCES / selected_reference
        st.caption(str(ref_path))
        st.audio(str(ref_path))
    if clone_packages:
        st.markdown("### Clone package preview")
        selected_clone = st.selectbox("Select clone package", [path.name for path in clone_packages])
        st.json(safe_read_json(VOICE_CLONE_PACKAGES / selected_clone, {}))
    if packages:
        st.markdown("### Standard package preview")
        selected_package = st.selectbox("Select package", [path.name for path in packages])
        st.json(safe_read_json(VOICE_PACKAGES / selected_package, {}))
    if files:
        selected = st.selectbox("Select voice file", [path.name for path in files])
        path = VOICE_OUTPUTS / selected
        st.caption(str(path))
        st.text_area("Preview", path.read_text(encoding="utf-8", errors="ignore"), height=420)
    else:
        st.info("No voice text files saved yet.")


def render_status() -> None:
    st.header("Status")
    ensure_dirs()
    files = list(VOICE_OUTPUTS.glob("*.txt"))
    packages = list(VOICE_PACKAGES.glob("*.json"))
    clone_packages = list(VOICE_CLONE_PACKAGES.glob("*.json"))
    audio_files = [path for path in AUDIO_OUTPUTS.glob("*") if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS]
    reference_files = list_files(VOICE_REFERENCES, AUDIO_EXTENSIONS)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Phase", PHASE)
    c2.metric("Status", PHASE_STATUS)
    c3.metric("Voice files", len(files))
    c4.metric("Packages", len(packages) + len(clone_packages))
    c5.metric("Reference voices", len(reference_files))
    st.success("Voice Workstation status: clone-ready with safer reference manager")
    st.markdown("### Voice clone safety rules")
    st.json(CLONE_SAFETY_RULES)
    st.markdown("### Voice project defaults")
    st.json(PROJECT_DEFAULTS)
    with st.expander("Paths", expanded=False):
        st.write({"voice_outputs": str(VOICE_OUTPUTS), "voice_directions": str(VOICE_DIRECTIONS), "voice_packages": str(VOICE_PACKAGES), "voice_clone_packages": str(VOICE_CLONE_PACKAGES), "voice_references": str(VOICE_REFERENCES), "audio_outputs": str(AUDIO_OUTPUTS), "workstation_links_json": str(WORKSTATION_LINKS_JSON)})


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("Voice Workstation Phase 4.5 is clone-ready with a safer reference manager for authorized reference voice planning, narration direction, TTS direction, package JSON, and future audio metadata.")
    st.markdown("This phase does not clone or generate voice yet. It prepares safe metadata for a future backend.")
    st.code("streamlit run voice_workstation/app.py --server.port 8504 --server.address 0.0.0.0", language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Voice Workstation", page_icon="🎙️", layout="wide")
    st.title("🎙️ Naz Lab Voice Workstation")
    st.caption("Phase 4.5 clone-ready — safer authorized reference voice manager, narration, TTS direction, package JSON.")
    st.success("Voice Workstation status: clone-ready with safer reference manager")
    st.info("Bangla-first voice workflow. Voice cloning requires user-provided or explicitly authorized reference audio.")
    ensure_dirs()
    update_workstation_status(WORKSTATION_LINKS_JSON, "voice_workstation", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    tabs = st.tabs(["Status", "Builder", "Library", "Launch"])
    with tabs[0]: render_status()
    with tabs[1]: render_builder()
    with tabs[2]: render_library()
    with tabs[3]: render_launch()


if __name__ == "__main__":
    main()
