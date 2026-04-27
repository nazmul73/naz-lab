"""Naz Lab Project Workflow Workstation Phase 10.0.

Foundation app for creating project-specific end-to-end package plans
for True Noir Tales and ToolFlow.
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

PHASE = "10.0"
PHASE_STATUS = "foundation"
PROJECT_PACKAGES = BASE_PATH / "project_packages"
PROJECT_WORKFLOWS = BASE_PATH / "project_workflows"

PROJECTS = ["True Noir Tales", "ToolFlow", "General"]
LANGUAGES = ["Bangla", "English", "Mixed Bangla-English"]
PLATFORMS = ["Facebook post", "Facebook Reel", "Carousel", "Story", "Full package"]
PACKAGE_STATUS = ["draft", "ready_for_production", "in_progress", "published", "archived"]

PROJECT_DEFAULTS = {
    "True Noir Tales": {
        "language": "English",
        "tone": "cinematic noir, suspenseful but restrained, adult-focused, psychology-aware",
        "safety": "adult-only, no gore, no dead body, no visible wounds, no sensational violence",
    },
    "ToolFlow": {
        "language": "English",
        "tone": "modern, clean, practical, premium, trustworthy, useful, non-hype",
        "safety": "no fake income claims, no spammy tone, no unverified AI news, no misleading UI",
    },
    "General": {
        "language": "Bangla",
        "tone": "natural spoken Bangla, Facebook-ready, netizen-friendly, voiceover-ready",
        "safety": "Bangla-first, practical, culturally grounded, no misleading claims",
    },
}


def ensure_dirs() -> None:
    PROJECT_PACKAGES.mkdir(parents=True, exist_ok=True)
    PROJECT_WORKFLOWS.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "project"


def list_json_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.glob("*.json") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)


def build_true_noir_package(topic: str, language: str, platform: str, audience: str, note: str) -> dict[str, Any]:
    bangla = language in {"Bangla", "Mixed Bangla-English"}
    hook = "ঘটনাটা বাইরে থেকে সাধারণ মনে হলেও, একটা ছোট detail পুরো গল্প বদলে দেয়।" if bangla else "What looked normal at first was hiding one detail that changed everything."
    cta = "তুমি হলে প্রথমে কোন জিনিসটা খেয়াল করতে?" if bangla else "What would you have noticed first?"
    script = {
        "hook": hook,
        "context": topic,
        "tension": "The most important clue is usually not the loudest one." if not bangla else "সবচেয়ে গুরুত্বপূর্ণ clue অনেক সময় সবচেয়ে চোখে পড়ার মতো হয় না।",
        "psychology_line": "People often miss warning signs when the situation looks familiar." if not bangla else "পরিচিত পরিস্থিতিতে মানুষ warning sign অনেক সময় মিস করে।",
        "cta": cta,
    }
    image_prompt = (
        "Realistic cinematic true crime noir scene, adult Bangladeshi subject, emotional tension, dramatic shadows, no gore, no blood, no dead body, no visible wounds, no sindoor unless requested."
    )
    voice_direction = "Suspenseful but restrained documentary narration, calm, clear, short dramatic pauses."
    video_direction = "5-scene reel: hook visual, context, critical detail, tension/reveal, question CTA. Cinematic suspense, readable subtitles."
    return {
        "script_package": script,
        "image_package": {"prompt": image_prompt, "format": "9:16 or 1:1", "negative": "no gore, no blood, no dead body, no visible wounds"},
        "voice_package": {"direction": voice_direction, "language": language},
        "video_package": {"direction": video_direction, "platform": platform},
        "posting_package": {"caption": hook, "cta": cta, "hashtags": ["#TrueCrime", "#CrimeStory", "#NoirStory", "#CrimePsychology"]},
        "notes": note,
        "audience": audience,
    }


def build_toolflow_package(topic: str, language: str, platform: str, audience: str, note: str) -> dict[str, Any]:
    bangla = language in {"Bangla", "Mixed Bangla-English"}
    hook = "AI tool আলাদা আলাদা ব্যবহার করলে ফল random হয়। system বানালে output পরিষ্কার হয়।" if bangla else "Random tools create random results. A simple system makes the output cleaner."
    cta = "তুমি কি এই workflowটা ব্যবহার করবে?" if bangla else "Would you use this workflow?"
    post = {
        "hook": hook,
        "problem": "Most people use tools without a repeatable workflow." if not bangla else "অনেকে tool ব্যবহার করে, কিন্তু repeatable workflow বানায় না।",
        "solution": topic,
        "steps": ["Define the goal", "Pick the tool", "Use a repeatable prompt/workflow", "Save the result"],
        "cta": cta,
    }
    image_prompt = "Clean modern SaaS/productivity visual, workspace or dashboard context, premium minimal composition, no fake logos, no misleading UI."
    voice_direction = "Practical creator explainer voice, clear pacing, confident but non-hype."
    video_direction = "5-scene explainer: messy workflow, tool/system intro, steps, result, CTA. Clean cuts and readable subtitles."
    return {
        "main_post_package": post,
        "carousel_package": {"slides": ["Hook", "Problem", "Workflow", "Step 1", "Step 2", "Step 3", "Result", "CTA"]},
        "reel_package": {"hook": hook, "target_length": "30 seconds", "cta": cta},
        "image_package": {"prompt": image_prompt, "format": "1:1, 4:5, or 9:16"},
        "voice_package": {"direction": voice_direction, "language": language},
        "video_package": {"direction": video_direction, "platform": platform},
        "posting_package": {"caption": hook, "cta": cta, "hashtags": ["#AITools", "#Productivity", "#Automation", "#SaaS", "#Workflow", "#ToolFlow"]},
        "notes": note,
        "audience": audience,
    }


def build_general_package(topic: str, language: str, platform: str, audience: str, note: str) -> dict[str, Any]:
    hook = "এই কথাটা অনেকেই খেয়াল করে না।"
    cta = "তোমার কী মনে হয়?"
    return {
        "text_package": {"hook": hook, "body": topic, "cta": cta},
        "image_package": {"prompt": "Natural Bangladeshi social content visual, realistic, culturally grounded, no misleading elements."},
        "voice_package": {"direction": "Natural spoken Bangla, Facebook-ready, voiceover-ready, clear pauses.", "language": language},
        "video_package": {"direction": "Hook-context-value-CTA video package, subtitle-friendly Bangla.", "platform": platform},
        "posting_package": {"caption": hook, "cta": cta, "hashtags": ["#BanglaContent", "#FacebookContent"]},
        "notes": note,
        "audience": audience,
    }


def build_package(project: str, topic: str, language: str, platform: str, audience: str, status: str, note: str) -> dict[str, Any]:
    if project == "True Noir Tales":
        body = build_true_noir_package(topic, language, platform, audience, note)
    elif project == "ToolFlow":
        body = build_toolflow_package(topic, language, platform, audience, note)
    else:
        body = build_general_package(topic, language, platform, audience, note)
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "phase": PHASE,
        "project_preset": project,
        "language": language,
        "platform": platform,
        "audience": audience,
        "topic": topic,
        "status": status,
        "project_defaults": PROJECT_DEFAULTS[project],
        "package": body,
        "global_rule": "Naz Lab is Bangla-first by default. English is supported for True Noir Tales and ToolFlow project presets.",
    }


def save_package(package: dict[str, Any]) -> Path:
    ensure_dirs()
    path = PROJECT_PACKAGES / f"project_package_{safe_name(package['project_preset'])}_{now_stamp()}.json"
    safe_write_json(path, package)
    append_output_log(OUTPUT_LOG_JSON, workstation="project_workstation", event="project_package_saved", details={"path": str(path), "project": package["project_preset"], "status": package["status"]})
    return path


def render_status() -> None:
    st.header("Status")
    ensure_dirs()
    packages = list_json_files(PROJECT_PACKAGES)
    c1, c2, c3 = st.columns(3)
    c1.metric("Phase", PHASE)
    c2.metric("Status", PHASE_STATUS)
    c3.metric("Project packages", len(packages))
    st.info("Project Workflow Workstation creates full package plans from one topic. It does not generate media directly.")
    st.json(PROJECT_DEFAULTS)


def render_builder() -> None:
    st.header("Project workflow builder")
    project = st.selectbox("Project", PROJECTS)
    defaults = PROJECT_DEFAULTS[project]
    language = st.selectbox("Language", LANGUAGES, index=LANGUAGES.index(defaults["language"]))
    platform = st.selectbox("Platform", PLATFORMS)
    status = st.selectbox("Package status", PACKAGE_STATUS)
    audience = st.text_input("Target audience", value="Facebook audience")
    topic = st.text_area("Topic / story / tool / idea", height=180, placeholder="Paste one topic, story idea, tool name, or workflow idea here.")
    note = st.text_area("Custom direction", height=100, placeholder="Example: more suspense, more Bangla, more practical, shorter reel, etc.")

    if not topic.strip():
        st.warning("Add a topic to generate a package preview.")
        return

    package = build_package(project, topic, language, platform, audience, status, note)
    st.markdown("### Package preview")
    st.json(package)
    st.text_area("Copy-ready package JSON", str(package), height=360)
    if st.button("Save project package JSON"):
        st.success(f"Saved: {save_package(package)}")


def render_library() -> None:
    st.header("Project package library")
    ensure_dirs()
    packages = list_json_files(PROJECT_PACKAGES)
    st.metric("Saved packages", len(packages))
    if packages:
        selected = st.selectbox("Select package", [p.name for p in packages])
        st.json(safe_read_json(PROJECT_PACKAGES / selected, {}))
    else:
        st.info("No project packages saved yet.")


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("Phase 10.0 creates project workflow packages for True Noir Tales, ToolFlow, and General content.")
    st.code("streamlit run project_workstation/app.py --server.port 8507 --server.address 0.0.0.0", language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Project Workflow Workstation", page_icon="🧩", layout="wide")
    st.title("🧩 Naz Lab Project Workflow Workstation")
    st.caption("Phase 10.0 foundation — one topic to full project package plan.")
    st.info("Naz Lab is Bangla-first by default. True Noir Tales and ToolFlow can stay English-first project presets.")
    ensure_dirs()
    update_workstation_status(WORKSTATION_LINKS_JSON, "project_workstation", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    tabs = st.tabs(["Status", "Builder", "Library", "Launch"])
    with tabs[0]: render_status()
    with tabs[1]: render_builder()
    with tabs[2]: render_library()
    with tabs[3]: render_launch()


if __name__ == "__main__":
    main()
