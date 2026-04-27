"""Naz Lab Portrait Workstation Phase 6.1.

Polished portrait package builder for Bangla-first social portraits,
True Noir Tales characters, ToolFlow creator portraits, personal portraits,
reference policy, style guidance, and future backend placeholders.
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
from shared.json_utils import append_output_log, safe_read_json, safe_write_json, update_workstation_status  # noqa: E402

PHASE = "6.1"
PORTRAIT_PACKAGES = BASE_PATH / "portrait_packages"
PORTRAIT_OUTPUTS = BASE_PATH / "portrait_outputs"
PORTRAIT_REFERENCES = BASE_PATH / "portrait_references"
IMAGE_JOBS = BASE_PATH / "image_jobs"
IMAGE_OUTPUTS = BASE_PATH / "image_outputs"

PROJECT_PRESETS = ["General", "True Noir Tales", "ToolFlow", "Personal portrait"]
LANGUAGE_OPTIONS = ["Bangla", "English", "Mixed Bangla-English"]
PORTRAIT_TYPES = ["Profile portrait", "Social media portrait", "Story character portrait", "Creator portrait", "Brand avatar", "Reference-based portrait plan"]
VISUAL_STYLES = ["realistic cinematic", "documentary realistic", "clean professional", "true crime noir", "premium social", "raw mobile-photo style", "editorial portrait", "creator thumbnail portrait"]
SCENARIOS = ["Auto by context", "Urban Bangladesh", "Rangpur/Nilphamari/North Bengal", "Dhaka city", "Office/workstation", "Home interior", "Studio portrait", "Street documentary", "Market/cafe", "Custom"]
FACE_POLICIES = ["Use reference only if user provided one", "No face reference", "Future reference workflow"]
OUTPUT_FORMATS = ["1:1 square", "4:5 portrait", "9:16 vertical", "16:9 wide", "Auto by context"]
MOOD_OPTIONS = ["natural confident", "calm serious", "cinematic tense", "friendly professional", "thoughtful", "premium clean", "emotional but controlled"]
CAMERA_STYLES = ["close-up", "medium portrait", "environmental portrait", "shallow depth of field", "cinematic side light", "natural phone-photo framing"]
PACKAGE_STATUS = ["draft", "ready_for_generation", "generated", "blocked", "archived"]

SAFETY_RULES = {
    "Consent/reference": "Use a personal face reference only when the user provides it for this workflow.",
    "Adults": "Use adult subjects only for content packages unless a safe family/photo-restoration workflow is explicitly designed later.",
    "Bangladesh realism": "Use Bangladeshi people and scenarios by default for general Naz Lab content.",
    "No sindoor default": "For women, no sindoor/vermilion unless explicitly requested.",
    "No gore": "No gore, no dead body, no visible wounds, no exposed violence.",
    "No fake official marks": "Avoid fake logos, fake official uniforms, fake documents, and misleading institutional marks.",
    "No identity guessing": "Do not claim or invent identity for real people in images.",
}

PROJECT_DEFAULTS = {
    "General": {
        "language": "Bangla",
        "style": "Bangla-first social portrait planning. Natural, culturally Bangladeshi, Facebook-ready, clean and realistic.",
        "default_scenario": "Rangpur/Nilphamari/North Bengal",
        "default_mood": "natural confident",
    },
    "True Noir Tales": {
        "language": "English",
        "style": "English true crime/noir adult character portrait. Moody, cinematic, tense, no gore, no dead body, no visible wounds.",
        "default_scenario": "Urban Bangladesh",
        "default_mood": "cinematic tense",
    },
    "ToolFlow": {
        "language": "English",
        "style": "English clean creator/productivity portrait. Professional, modern, premium, practical, non-hype.",
        "default_scenario": "Office/workstation",
        "default_mood": "friendly professional",
    },
    "Personal portrait": {
        "language": "Bangla",
        "style": "Reference-aware personal portrait planning. Use only user-provided reference, keep natural and respectful.",
        "default_scenario": "Studio portrait",
        "default_mood": "natural confident",
    },
}


def ensure_dirs() -> None:
    PORTRAIT_PACKAGES.mkdir(parents=True, exist_ok=True)
    PORTRAIT_OUTPUTS.mkdir(parents=True, exist_ok=True)
    PORTRAIT_REFERENCES.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "portrait"


def list_json_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.glob("*.json") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)


def list_image_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    extensions = {".png", ".jpg", ".jpeg", ".webp"}
    return sorted([p for p in folder.glob("*") if p.is_file() and p.suffix.lower() in extensions], key=lambda p: p.stat().st_mtime, reverse=True)


def suggested_output_filename(project: str, portrait_type: str) -> str:
    return f"{safe_name(project)}_{safe_name(portrait_type)}_{now_stamp()}.png"


def build_style_notes(project: str, language: str, mood: str, camera_style: str) -> str:
    notes = [
        f"Mood: {mood}",
        f"Camera style: {camera_style}",
        "Skin texture should look natural, not plastic or over-smoothed.",
        "Expression should feel human and believable.",
    ]
    if language in {"Bangla", "Mixed Bangla-English"}:
        notes.append("Planning language should support natural Bangla caption/story usage.")
    if project == "True Noir Tales":
        notes.append("Use noir lighting, emotional tension, adult character framing, and subtle storytelling details.")
    if project == "ToolFlow":
        notes.append("Use clean workspace, productivity/AI context, premium minimal look, and non-hype creator framing.")
    if project == "Personal portrait":
        notes.append("Keep respectful, natural, and consistent with user-provided reference only.")
    return "\n".join(notes)


def build_positive_prompt(project: str, language: str, portrait_type: str, style: str, scenario: str, face_policy: str, output_format: str, mood: str, camera_style: str, topic: str, custom_note: str) -> str:
    style_notes = build_style_notes(project, language, mood, camera_style)
    parts = [
        f"Project preset: {project}",
        f"Language/planning: {language}",
        f"Portrait type: {portrait_type}",
        f"Visual style: {style}",
        f"Scenario: {scenario}",
        f"Mood: {mood}",
        f"Camera style: {camera_style}",
        f"Face/reference policy: {face_policy}",
        f"Output format: {output_format}",
        f"Project style: {PROJECT_DEFAULTS[project]['style']}",
        "Bangla-first rule: General Naz Lab planning defaults to Bangla; English is used for selected English projects or when requested.",
        "Create a realistic, natural, culturally grounded portrait plan with adult subjects only.",
        "Bangladeshi people and Bangladeshi scenario by default for General Naz Lab content.",
        "Urban and rural Bangladesh are both allowed depending on scenario.",
        "For women, no sindoor or vermilion in hair parting unless explicitly requested.",
        style_notes,
    ]
    if project == "True Noir Tales":
        parts.append("True Noir Tales portrait rule: moody true-crime noir, adult character, emotional tension, no gore, no dead body, no visible wounds, no exposed violence.")
    if project == "ToolFlow":
        parts.append("ToolFlow portrait rule: clean modern professional creator/productivity feel, premium but non-hype, practical and trustworthy.")
    if topic.strip():
        parts.append(f"Source/topic:\n{topic.strip()}")
    if custom_note.strip():
        parts.append(f"Custom direction:\n{custom_note.strip()}")
    return "\n\n".join(parts)


def build_negative_prompt(project: str) -> str:
    base = [
        "no gore",
        "no dead body",
        "no visible wounds",
        "no exposed violence",
        "no distorted face",
        "no extra fingers",
        "no fake logo",
        "no watermark",
        "no unreadable text",
        "no sindoor unless explicitly requested",
        "no vermilion unless explicitly requested",
        "no misleading official uniform or document",
        "no plastic skin",
        "no over-smoothed face",
    ]
    if project == "True Noir Tales":
        base.extend(["no blood", "no weapon focus", "no sensational violence"])
    return ", ".join(base)


def build_package(project: str, language: str, portrait_type: str, style: str, scenario: str, face_policy: str, output_format: str, mood: str, camera_style: str, status: str, output_path: str, positive: str, negative: str) -> dict[str, Any]:
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "phase": PHASE,
        "project_preset": project,
        "language": language,
        "portrait_type": portrait_type,
        "visual_style": style,
        "scenario": scenario,
        "mood": mood,
        "camera_style": camera_style,
        "face_policy": face_policy,
        "output_format": output_format,
        "status": status,
        "suggested_output_path": output_path,
        "positive_prompt": positive,
        "negative_prompt": negative,
        "combined_prompt": f"POSITIVE PROMPT:\n{positive}\n\nNEGATIVE PROMPT:\n{negative}",
        "future_backend": "placeholder",
    }


def save_package(package: dict[str, Any]) -> Path:
    ensure_dirs()
    path = PORTRAIT_PACKAGES / f"portrait_package_{safe_name(package['project_preset'])}_{now_stamp()}.json"
    safe_write_json(path, package)
    append_output_log(OUTPUT_LOG_JSON, workstation="portrait_workstation", event="portrait_package_saved", details={"path": str(path), "project": package["project_preset"], "status": package["status"]})
    return path


def render_status() -> None:
    st.header("Status")
    ensure_dirs()
    packages = list_json_files(PORTRAIT_PACKAGES)
    outputs = list_image_files(PORTRAIT_OUTPUTS)
    references = list_image_files(PORTRAIT_REFERENCES)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Phase", PHASE)
    c2.metric("Packages", len(packages))
    c3.metric("Portrait outputs", len(outputs))
    c4.metric("Reference images", len(references))
    st.info("Phase 6.1 polishes portrait presets and prompt packages. It does not run a portrait backend yet.")
    st.markdown("### Safety rules")
    st.json(SAFETY_RULES)
    st.markdown("### Project defaults")
    st.json(PROJECT_DEFAULTS)
    with st.expander("Paths", expanded=False):
        st.write({"portrait_packages": str(PORTRAIT_PACKAGES), "portrait_outputs": str(PORTRAIT_OUTPUTS), "portrait_references": str(PORTRAIT_REFERENCES), "image_jobs": str(IMAGE_JOBS), "image_outputs": str(IMAGE_OUTPUTS)})


def render_builder() -> None:
    st.header("Portrait package builder")
    project = st.selectbox("Project preset", PROJECT_PRESETS)
    defaults = PROJECT_DEFAULTS[project]
    language = st.selectbox("Language", LANGUAGE_OPTIONS, index=LANGUAGE_OPTIONS.index(defaults["language"]))
    portrait_type = st.selectbox("Portrait type", PORTRAIT_TYPES)
    style = st.selectbox("Visual style", VISUAL_STYLES)
    default_scenario = defaults["default_scenario"] if defaults["default_scenario"] in SCENARIOS else "Auto by context"
    scenario = st.selectbox("Scenario", SCENARIOS, index=SCENARIOS.index(default_scenario))
    mood = st.selectbox("Mood", MOOD_OPTIONS, index=MOOD_OPTIONS.index(defaults["default_mood"]))
    camera_style = st.selectbox("Camera style", CAMERA_STYLES)
    face_policy = st.selectbox("Face/reference policy", FACE_POLICIES)
    output_format = st.selectbox("Output format", OUTPUT_FORMATS)
    status = st.selectbox("Package status", PACKAGE_STATUS)
    suggested_output = PORTRAIT_OUTPUTS / suggested_output_filename(project, portrait_type)
    output_path = st.text_input("Suggested portrait output path", value=str(suggested_output))
    topic = st.text_area("Source topic / character description", height=150, placeholder="Describe the person/character/brand portrait need here.")
    custom_note = st.text_area("Custom portrait direction", height=100, placeholder="Example: more professional, more emotional, more North Bengal realism, etc.")
    positive = build_positive_prompt(project, language, portrait_type, style, scenario, face_policy, output_format, mood, camera_style, topic, custom_note)
    negative = build_negative_prompt(project)
    package = build_package(project, language, portrait_type, style, scenario, face_policy, output_format, mood, camera_style, status, output_path, positive, negative)
    st.markdown("### Reference workflow note")
    st.warning("Use a face reference only when the user provides one for this workflow. Do not assume or invent a specific real person's face.")
    st.text_area("Positive prompt", positive, height=300)
    st.text_area("Negative prompt", negative, height=130)
    st.text_area("Combined prompt", package["combined_prompt"], height=380)
    with st.expander("Portrait package JSON preview", expanded=False):
        st.json(package)
    if st.button("Save portrait package JSON"):
        st.success(f"Saved: {save_package(package)}")


def render_library() -> None:
    st.header("Portrait package library")
    ensure_dirs()
    packages = list_json_files(PORTRAIT_PACKAGES)
    outputs = list_image_files(PORTRAIT_OUTPUTS)
    references = list_image_files(PORTRAIT_REFERENCES)
    st.metric("Packages", len(packages))
    st.metric("Outputs", len(outputs))
    st.metric("References", len(references))
    if packages:
        selected = st.selectbox("Select package", [p.name for p in packages])
        st.json(safe_read_json(PORTRAIT_PACKAGES / selected, {}))
    if outputs:
        st.markdown("### Output files")
        for item in outputs[:10]:
            st.write(str(item))
    if references:
        st.markdown("### Reference files")
        for item in references[:10]:
            st.write(str(item))
    if not packages:
        st.info("No portrait packages saved yet.")


def render_inputs() -> None:
    st.header("Input placeholders")
    st.markdown("Future versions may connect image jobs, portrait references, and generated outputs directly.")
    image_jobs = list_json_files(IMAGE_JOBS)
    image_outputs = list_image_files(IMAGE_OUTPUTS)
    st.write({"image_job_count": len(image_jobs), "image_output_count": len(image_outputs)})
    if image_jobs:
        selected_job = st.selectbox("Preview image job", [p.name for p in image_jobs])
        st.json(safe_read_json(IMAGE_JOBS / selected_job, {}))


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("Phase 6.1 creates polished portrait planning packages. It does not generate or swap faces.")
    st.markdown("Future build: reference image manager, output path validation, and optional backend planning.")
    st.code("streamlit run portrait_workstation/app.py --server.port 8506 --server.address 0.0.0.0", language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Portrait Workstation", page_icon="🧑", layout="wide")
    st.title("🧑 Naz Lab Portrait Workstation")
    st.caption("Phase 6.1 — polished portrait presets, safety rules, prompt packages, future backend placeholder.")
    st.info("Bangla-first planning. Use face references only when the user provides them for this workflow.")
    ensure_dirs()
    update_workstation_status(WORKSTATION_LINKS_JSON, "portrait_workstation", {"status": "running", "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    tabs = st.tabs(["Status", "Builder", "Inputs", "Library", "Launch"])
    with tabs[0]: render_status()
    with tabs[1]: render_builder()
    with tabs[2]: render_inputs()
    with tabs[3]: render_library()
    with tabs[4]: render_launch()


if __name__ == "__main__":
    main()
