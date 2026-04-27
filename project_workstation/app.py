"""Naz Lab Project Workflow Workstation Phase 10.2 stable.

Stable app for creating project-specific end-to-end package plans
for True Noir Tales, ToolFlow, and General Bangla-first content.
"""

from __future__ import annotations

import json
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

PHASE = "10.2"
PHASE_STATUS = "stable"
PROJECT_PACKAGES = BASE_PATH / "project_packages"
PROJECT_WORKFLOWS = BASE_PATH / "project_workflows"

PROJECTS = ["True Noir Tales", "ToolFlow", "General"]
LANGUAGES = ["Bangla", "English", "Mixed Bangla-English"]
PLATFORMS = ["Facebook post", "Facebook Reel", "Carousel", "Story", "Full package"]
PACKAGE_STATUS = ["draft", "ready_for_production", "in_progress", "published", "archived"]

BANGLA_RULE = "Bangla must be natural spoken Bangla, Facebook-ready, netizen-friendly, voiceover-ready, simple, human, and not stiff textbook Bangla. Default regional flavor: Rangpur/Nilphamari/North Bengal, used lightly."
REFERENCE_POLICY = "Use face/voice references only when user-provided or explicitly authorized. Do not use misleading or unauthorized reference assets."

PROJECT_DEFAULTS = {
    "True Noir Tales": {
        "language": "English",
        "tone": "cinematic noir, suspenseful but restrained, adult-focused, psychology-aware",
        "safety": "adult-only, no gore, no dead body, no visible wounds, no sensational violence",
        "best_for": "true crime, mystery, noir story, psychology-driven storytelling",
    },
    "ToolFlow": {
        "language": "English",
        "tone": "modern, clean, practical, premium, trustworthy, useful, non-hype",
        "safety": "no fake income claims, no spammy tone, no unverified AI news, no misleading UI",
        "best_for": "AI tools, SaaS, automation, productivity workflows",
    },
    "General": {
        "language": "Bangla",
        "tone": "natural spoken Bangla, Facebook-ready, netizen-friendly, voiceover-ready",
        "safety": "Bangla-first, practical, culturally grounded, no misleading claims",
        "best_for": "Bangla Facebook posts, reels, captions, social content packages",
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


def to_pretty_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_true_noir_package(topic: str, language: str, platform: str, audience: str, note: str) -> dict[str, Any]:
    bangla = language in {"Bangla", "Mixed Bangla-English"}
    if bangla:
        title = "যে detailটা সবাই মিস করেছিল"
        hook = "সবাই ঘটনাটাকে সাধারণ ভেবেছিল। কিন্তু একটা ছোট detail পুরো গল্পটার মানে বদলে দেয়।"
        context_line = topic
        tension = "সবচেয়ে গুরুত্বপূর্ণ clue অনেক সময় সবচেয়ে চোখে পড়ার মতো হয় না।"
        reveal = "এই জায়গাতেই গল্পটা শুধু ঘটনা থাকে না, মানুষের মনস্তত্ত্বের প্রশ্ন হয়ে দাঁড়ায়।"
        psychology_line = "পরিচিত পরিস্থিতিতে মানুষ warning sign অনেক সময় মিস করে, কারণ মস্তিষ্ক আগে থেকেই ধরে নেয় সবকিছু স্বাভাবিক।"
        cta = "তুমি হলে প্রথমে কোন detailটা খেয়াল করতে?"
        caption = "একটা ছোট detail কখনো কখনো পুরো গল্প বদলে দিতে পারে। তুমি হলে কোন জিনিসটা আগে ধরতে?"
    else:
        title = "The Detail Everyone Missed"
        hook = "Everyone thought it was ordinary. But one small detail changed the meaning of the entire story."
        context_line = topic
        tension = "The most important clue is usually not the loudest one. It is the one people explain away too quickly."
        reveal = "That is where the story stops being just an incident and becomes a question about human behavior."
        psychology_line = "People often miss warning signs when a situation feels familiar, because the brain tries to protect the version of reality it already believes."
        cta = "What would you have noticed first?"
        caption = "One small detail can change the entire story. What would you have noticed first?"

    script = {
        "title": title,
        "hook": hook,
        "context": context_line,
        "tension": tension,
        "turn_or_reveal": reveal,
        "psychology_line": psychology_line,
        "cta": cta,
        "voiceover_structure": ["0-3s hook", "3-12s context", "12-25s tension", "25-40s psychology/reveal", "40-45s question CTA"],
    }
    image_prompt = (
        "Realistic cinematic true crime noir scene, adult Bangladeshi subject, emotionally tense human-centered composition, "
        "urban or semi-urban Bangladesh setting, moody lighting, dramatic shadows, shallow depth of field, grounded environment, "
        "subtle storytelling detail in the scene, premium social media aesthetic, no gore, no blood, no dead body, no visible wounds, "
        "no exposed violence, no police logo, no watermark, no fake official marks, no sindoor unless explicitly requested."
    )
    voice_direction = "Suspenseful but restrained documentary narration, calm, clear, short dramatic pauses, controlled emotion, no overacting."
    if bangla:
        voice_direction += " Use natural spoken Bangla, voiceover-ready, simple and emotional, not stiff textbook Bangla; light Rangpur/Nilphamari flavor only if it fits naturally."
    video_direction = (
        "5-scene reel: Scene 1 hook visual with tense close-up; Scene 2 context visual; Scene 3 small critical detail; "
        "Scene 4 psychology/reveal; Scene 5 question CTA. Cinematic suspense, subtle zooms, readable subtitles, dark restrained music, no graphic visuals."
    )
    return {
        "script_package": script,
        "image_package": {"prompt": image_prompt, "format": "9:16 Reel, 1:1 post, or 4:5 Facebook/Instagram", "negative": "no gore, no blood, no dead body, no visible wounds, no sensational violence, no fake logo, no sindoor unless requested"},
        "voice_package": {"direction": voice_direction, "language": language, "reference_policy": REFERENCE_POLICY},
        "video_package": {"direction": video_direction, "platform": platform, "scene_sequence": ["Hook visual", "Context", "Critical detail", "Psychology/reveal", "Question CTA"], "subtitle_note": "Keep subtitles short, mobile-readable, and matched to pauses."},
        "posting_package": {"caption": caption, "cta": cta, "hashtags": ["#TrueCrime", "#CrimeStory", "#NoirStory", "#CrimePsychology", "#MysteryStory"]},
        "safety_notes": ["adult-focused", "no gore", "no dead body", "no visible wounds", "no sensational violence"],
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
        "steps": ["Define the goal", "Pick the tool", "Use a repeatable prompt/workflow", "Save and reuse the result"],
        "verdict": "Use tools as a system, not as random shortcuts." if not bangla else "Tool random ভাবে না, system হিসেবে ব্যবহার করলেই ফল ভালো হয়।",
        "cta": cta,
    }
    image_prompt = "Clean modern SaaS/productivity visual, workspace or dashboard context, premium minimal composition, practical creator feel, no fake logos, no misleading UI, no clutter."
    voice_direction = "Practical creator explainer voice, clear pacing, confident but non-hype, clean sentence breaks."
    if bangla:
        voice_direction += " Use natural spoken Bangla, simple, practical, and beginner-friendly."
    video_direction = "5-scene explainer: messy workflow/problem, tool/system intro, 2-3 practical steps, result/benefit, CTA. Clean cuts and readable subtitles."
    return {
        "main_post_package": post,
        "carousel_package": {"slides": ["Hook / promise", "Problem", "Workflow", "Step 1", "Step 2", "Step 3", "Result", "CTA"]},
        "reel_package": {"hook": hook, "target_length": "30 seconds", "cta": cta, "scene_sequence": ["Problem", "System", "Steps", "Result", "CTA"]},
        "image_package": {"prompt": image_prompt, "format": "1:1, 4:5, or 9:16", "negative": "no fake logos, no misleading UI, no clutter, no unreadable text"},
        "voice_package": {"direction": voice_direction, "language": language, "reference_policy": REFERENCE_POLICY},
        "video_package": {"direction": video_direction, "platform": platform},
        "posting_package": {"caption": hook, "cta": cta, "hashtags": ["#AITools", "#Productivity", "#Automation", "#SaaS", "#Workflow", "#ToolFlow"]},
        "notes": note,
        "audience": audience,
    }


def build_general_package(topic: str, language: str, platform: str, audience: str, note: str) -> dict[str, Any]:
    hook = "এই কথাটা অনেকেই খেয়াল করে না।"
    cta = "তোমার কী মনে হয়?"
    return {
        "text_package": {"hook": hook, "body": topic, "cta": cta, "bangla_rule": BANGLA_RULE},
        "image_package": {"prompt": "Natural Bangladeshi social content visual, realistic, culturally grounded, urban or rural Bangladesh as appropriate, no misleading elements, no sindoor unless requested."},
        "voice_package": {"direction": "Natural spoken Bangla, Facebook-ready, voiceover-ready, clear pauses, one idea per sentence.", "language": language, "reference_policy": REFERENCE_POLICY},
        "video_package": {"direction": "Hook-context-value-CTA video package, subtitle-friendly Bangla, short mobile-readable lines.", "platform": platform},
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
        "bangla_quality_rule": BANGLA_RULE,
        "reference_policy": REFERENCE_POLICY,
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
    ready = sum(1 for path in packages if safe_read_json(path, {}).get("status") == "ready_for_production")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Phase", PHASE)
    c2.metric("Status", PHASE_STATUS)
    c3.metric("Project packages", len(packages))
    c4.metric("Ready packages", ready)
    st.success("Project Workflow Workstation status: stable for Phase 10")
    st.info("Creates full package plans from one topic. It does not generate media directly.")
    st.markdown("### Stable workflow")
    st.markdown("1. Pick project preset.  \n2. Choose language and platform.  \n3. Paste one topic/story/tool idea.  \n4. Review Script/Image/Voice/Video/Posting tabs.  \n5. Save project package JSON.")
    st.markdown("### Safety and quality")
    st.write(BANGLA_RULE)
    st.write(REFERENCE_POLICY)
    with st.expander("Project defaults", expanded=False):
        st.json(PROJECT_DEFAULTS)
    with st.expander("Paths", expanded=False):
        st.write({"project_packages": str(PROJECT_PACKAGES), "project_workflows": str(PROJECT_WORKFLOWS)})


def render_package_sections(package: dict[str, Any]) -> None:
    body = package.get("package", {})
    tabs = st.tabs(["Script/Post", "Image", "Voice", "Video", "Posting", "JSON"])
    with tabs[0]:
        st.json(body.get("script_package", body.get("main_post_package", body.get("text_package", {}))))
    with tabs[1]:
        st.json(body.get("image_package", {}))
        prompt = body.get("image_package", {}).get("prompt", "")
        if prompt:
            st.text_area("Copy image prompt", prompt, height=160)
    with tabs[2]:
        st.json(body.get("voice_package", {}))
        direction = body.get("voice_package", {}).get("direction", "")
        if direction:
            st.text_area("Copy voice direction", direction, height=160)
    with tabs[3]:
        st.json(body.get("video_package", {}))
        direction = body.get("video_package", {}).get("direction", "")
        if direction:
            st.text_area("Copy video direction", direction, height=160)
    with tabs[4]:
        st.json(body.get("posting_package", {}))
    with tabs[5]:
        st.text_area("Copy-ready package JSON", to_pretty_json(package), height=420)


def render_builder() -> None:
    st.header("Project workflow builder")
    project = st.selectbox("Project", PROJECTS)
    defaults = PROJECT_DEFAULTS[project]
    language = st.selectbox("Language", LANGUAGES, index=LANGUAGES.index(defaults["language"]))
    platform = st.selectbox("Platform", PLATFORMS)
    status = st.selectbox("Package status", PACKAGE_STATUS, index=PACKAGE_STATUS.index("ready_for_production"))
    audience = st.text_input("Target audience", value="Facebook audience")
    topic = st.text_area("Topic / story / tool / idea", height=180, placeholder="Paste one topic, story idea, tool name, or workflow idea here.")
    note = st.text_area("Custom direction", height=100, placeholder="Example: more suspense, more Bangla, more practical, shorter reel, etc.")

    if not topic.strip():
        st.warning("Add a topic to generate a package preview.")
        return

    package = build_package(project, topic, language, platform, audience, status, note)
    st.markdown("### Package preview")
    render_package_sections(package)
    if st.button("Save project package JSON"):
        saved = save_package(package)
        st.success(f"Saved: {saved}")


def render_library() -> None:
    st.header("Project package library")
    ensure_dirs()
    packages = list_json_files(PROJECT_PACKAGES)
    st.metric("Saved packages", len(packages))
    if packages:
        selected = st.selectbox("Select package", [p.name for p in packages])
        data = safe_read_json(PROJECT_PACKAGES / selected, {})
        render_package_sections(data)
    else:
        st.info("No project packages saved yet.")


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("Project Workflow Workstation Phase 10.2 is stable for one-topic-to-package planning.")
    st.code("streamlit run project_workstation/app.py --server.port 8507 --server.address 0.0.0.0", language="bash")
    st.markdown("Recommended all-in-one launcher value:")
    st.code('WORKSTATION="project"', language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Project Workflow Workstation", page_icon="🧩", layout="wide")
    st.title("🧩 Naz Lab Project Workflow Workstation")
    st.caption("Phase 10.2 stable — one topic to full project package plan.")
    st.success("Project Workflow Workstation status: stable for Phase 10")
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
