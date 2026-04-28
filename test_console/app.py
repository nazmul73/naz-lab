"""Naz Lab Input Test Console Phase 1.0.

Frontend-first testing console for Naz Lab v1 workflows.
This app is for entering topic/input and testing package outputs without using
backend commands directly.
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
from shared.json_utils import append_output_log, safe_write_json, update_workstation_status  # noqa: E402

PHASE = "1.0"
PHASE_STATUS = "frontend-input-test-console"

TEST_PACKAGES = BASE_PATH / "test_console_packages"
PROJECT_PACKAGES = BASE_PATH / "project_packages"
IMAGE_JOBS = BASE_PATH / "job_queue" / "image_jobs"
VOICE_JOBS = BASE_PATH / "job_queue" / "voice_jobs"
VIDEO_JOBS = BASE_PATH / "job_queue" / "video_jobs"
PORTRAIT_PACKAGES = BASE_PATH / "portrait_packages"
FINAL_REEL_PACKS = BASE_PATH / "final_reel_packs"

PROJECTS = ["General Bangla", "True Noir Tales", "ToolFlow"]
WORKFLOW_TYPES = [
    "Full Content Package",
    "Text / Script",
    "Image Prompt",
    "Voice / TTS Plan",
    "Portrait Prompt",
    "Video Scene Plan",
    "Final Reel Pack Manifest",
]
PLATFORMS = ["Facebook Reel", "Facebook Post", "Carousel", "Story", "Full Package"]
LANGUAGES = ["Bangla", "English", "Mixed Bangla-English"]

BANGLA_RULE = "Natural spoken Bangla, Facebook-ready, voiceover-ready, simple, human, not stiff textbook Bangla. Light Rangpur/Nilphamari/North Bengal flavor when useful."
SAFETY_RULE = "Adult-only when human subjects are used. No gore, no dead body, no visible wounds, no exposed violence, no unauthorized reference face/voice."
VIDEO_DEFERRED = "Real video generation is deferred after Naz Lab v1. This console creates video plans/manifests only."


def ensure_dirs() -> None:
    for folder in [TEST_PACKAGES, PROJECT_PACKAGES, IMAGE_JOBS, VOICE_JOBS, VIDEO_JOBS, PORTRAIT_PACKAGES, FINAL_REEL_PACKS]:
        folder.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "naz_lab_test"


def pretty(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def save_json(folder: Path, prefix: str, data: dict[str, Any]) -> Path:
    ensure_dirs()
    path = folder / f"{prefix}_{safe_name(data.get('project', data.get('workflow', 'test')))}_{now_stamp()}.json"
    safe_write_json(path, data)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="input_test_console",
        event="frontend_test_package_saved",
        details={"path": str(path), "workflow": data.get("workflow"), "project": data.get("project")},
    )
    return path


def build_text_package(project: str, topic: str, language: str, platform: str, audience: str, direction: str) -> dict[str, Any]:
    bangla = language != "English"
    if bangla:
        return {
            "title": "AI দিয়ে content বানানোর সহজ workflow",
            "hook": "প্রতিদিন content বানাতে গিয়ে যদি আটকে যান, তাহলে আগে tool না, একটা system দরকার।",
            "voiceover_script": [
                "প্রতিদিন নতুন idea খোঁজা কঠিন।",
                "কিন্তু AI tool ঠিকভাবে ব্যবহার করলে topic, caption, script আর visual plan এক জায়গায় সাজানো যায়।",
                "প্রথমে topic লিখুন। তারপর script বানান, image prompt বানান, voiceover তৈরি করুন।",
                "সবশেষে final package save করে রাখুন।",
                "আপনি কি এই workflow ব্যবহার করবেন?",
            ],
            "caption": "AI tool random ভাবে ব্যবহার না করে system বানালে content creation অনেক সহজ হয়। আপনি কি এই workflow try করবেন?",
            "cta": "আপনি কোন অংশ আগে automate করতে চান?",
            "hashtags": ["#BanglaContent", "#AITools", "#ContentCreation", "#FacebookReels"],
            "topic": topic,
            "audience": audience,
            "direction": direction,
            "quality_rule": BANGLA_RULE,
        }
    return {
        "title": "A simple AI content workflow",
        "hook": "If content creation feels slow, you do not need more tools first. You need a system.",
        "voiceover_script": [
            "Start with one topic.",
            "Turn it into a script, image prompt, voice direction, and posting package.",
            "Save the package so you can reuse the workflow again.",
            "Would you use this system?",
        ],
        "caption": "AI tools work better when you turn them into a repeatable system.",
        "cta": "Which part would you automate first?",
        "hashtags": ["#AITools", "#ContentCreation", "#Workflow"],
        "topic": topic,
        "audience": audience,
        "direction": direction,
    }


def build_image_package(project: str, topic: str, language: str, platform: str, direction: str) -> dict[str, Any]:
    if project == "True Noir Tales":
        prompt = (
            "Realistic cinematic true crime noir visual in Bangladesh, adult subject only, emotionally tense, moody lighting, "
            "dramatic shadows, human-centered composition, subtle storytelling detail, premium social media poster look, no gore, "
            "no blood, no dead body, no visible wounds, no exposed violence. Topic: " + topic
        )
    elif project == "ToolFlow":
        prompt = (
            "Clean modern productivity visual, adult creator using AI tools on laptop, premium SaaS aesthetic, organized workflow, "
            "minimal UI feeling, trustworthy non-hype look, no fake logos, no misleading UI. Topic: " + topic
        )
    else:
        prompt = (
            "Natural Bangladeshi social content visual, adult creator or small business owner, realistic cinematic photography, "
            "Facebook-ready composition, culturally grounded Bangladesh setting, warm practical mood, no fake logos, no misleading elements. Topic: " + topic
        )
    return {
        "positive_prompt": prompt,
        "negative_prompt": "no gore, no dead body, no visible wounds, no exposed violence, no fake logo, no watermark, no distorted face, no unauthorized reference face",
        "format": "1:1 square, 4:5 post, or 9:16 reel cover",
        "platform": platform,
        "language": language,
        "direction": direction,
        "safety_rule": SAFETY_RULE,
    }


def build_voice_package(topic: str, language: str, direction: str) -> dict[str, Any]:
    script = "আজ আমরা দেখব, কীভাবে AI tools ব্যবহার করে সহজভাবে content plan করা যায়। প্রথমে topic ঠিক করুন, তারপর script, image prompt আর voiceover একসাথে সাজান।"
    if language == "English":
        script = "Today we will see how to plan content with AI tools using a simple repeatable workflow."
    return {
        "voice_mode": "Original / generic voice direction",
        "language": language,
        "script_draft": script,
        "tts_direction": "Natural, clear, voiceover-ready, simple pacing.",
        "reference_voice_path": "",
        "reference_voice_authorized": False,
        "reference_policy": "Generic TTS only. No voice cloning in Naz Lab v1.",
        "topic": topic,
        "direction": direction,
    }


def build_portrait_package(topic: str, direction: str) -> dict[str, Any]:
    return {
        "portrait_type": "Generic professional portrait",
        "positive_prompt": "Realistic professional Bangladeshi adult creator portrait, clean social media profile image, natural expression, respectful, culturally grounded, premium but realistic.",
        "negative_prompt": "no gore, no visible wounds, no distorted face, no misleading identity claim, no unauthorized face reference, no watermark",
        "reference_image_path": "",
        "reference_image_authorized": False,
        "no_misleading_identity_claim": True,
        "reference_policy": "Reference image must be user-provided or explicitly authorized.",
        "topic": topic,
        "direction": direction,
    }


def build_video_plan(topic: str, platform: str, direction: str) -> dict[str, Any]:
    return {
        "video_generation_status": "deferred_after_v1",
        "note": VIDEO_DEFERRED,
        "platform": platform,
        "target_duration": "45-60 seconds",
        "scene_plan": [
            {"scene": 1, "purpose": "Hook", "visual": "Creator or topic-related opening shot", "text": "একটা simple system দরকার"},
            {"scene": 2, "purpose": "Problem", "visual": "Messy content planning moment", "text": "Random tool use করলে output এলোমেলো হয়"},
            {"scene": 3, "purpose": "Workflow", "visual": "Topic -> Script -> Image -> Voice", "text": "এক topic থেকে full package"},
            {"scene": 4, "purpose": "Result", "visual": "Organized final package", "text": "সব output এক জায়গায়"},
            {"scene": 5, "purpose": "CTA", "visual": "Final question screen", "text": "আপনি কোন workflow test করবেন?"},
        ],
        "topic": topic,
        "direction": direction,
    }


def build_final_pack(project: str, topic: str, language: str, platform: str, audience: str, direction: str) -> dict[str, Any]:
    text_pkg = build_text_package(project, topic, language, platform, audience, direction)
    image_pkg = build_image_package(project, topic, language, platform, direction)
    voice_pkg = build_voice_package(topic, language, direction)
    video_pkg = build_video_plan(topic, platform, direction)
    return {
        "phase": "Naz Lab Input Test Console 1.0",
        "status": "frontend_test_ready",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project": project,
        "workflow": "Full Content Package",
        "language": language,
        "platform": platform,
        "audience": audience,
        "topic": topic,
        "direction": direction,
        "text_package": text_pkg,
        "image_package": image_pkg,
        "voice_package": voice_pkg,
        "video_plan": video_pkg,
        "posting_package": {
            "caption": text_pkg.get("caption", ""),
            "cta": text_pkg.get("cta", ""),
            "hashtags": text_pkg.get("hashtags", []),
        },
        "safety_notes": [BANGLA_RULE, SAFETY_RULE, VIDEO_DEFERRED],
    }


def package_folder_for_workflow(workflow: str) -> tuple[Path, str]:
    if workflow == "Full Content Package":
        return PROJECT_PACKAGES, "frontend_full_package"
    if workflow == "Text / Script":
        return TEST_PACKAGES, "frontend_text"
    if workflow == "Image Prompt":
        return IMAGE_JOBS, "frontend_image"
    if workflow == "Voice / TTS Plan":
        return VOICE_JOBS, "frontend_voice"
    if workflow == "Portrait Prompt":
        return PORTRAIT_PACKAGES, "frontend_portrait"
    if workflow == "Video Scene Plan":
        return VIDEO_JOBS, "frontend_video"
    return FINAL_REEL_PACKS, "frontend_final_pack"


def build_selected_package(project: str, workflow: str, topic: str, language: str, platform: str, audience: str, direction: str) -> dict[str, Any]:
    base = {
        "phase": PHASE,
        "status": "frontend_test_ready",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project": project,
        "workflow": workflow,
        "language": language,
        "platform": platform,
        "audience": audience,
        "topic": topic,
        "direction": direction,
    }
    if workflow == "Full Content Package":
        return build_final_pack(project, topic, language, platform, audience, direction)
    if workflow == "Text / Script":
        base["text_package"] = build_text_package(project, topic, language, platform, audience, direction)
    elif workflow == "Image Prompt":
        base["image_package"] = build_image_package(project, topic, language, platform, direction)
    elif workflow == "Voice / TTS Plan":
        base["voice_package"] = build_voice_package(topic, language, direction)
    elif workflow == "Portrait Prompt":
        base["portrait_package"] = build_portrait_package(topic, direction)
    elif workflow == "Video Scene Plan":
        base["video_plan"] = build_video_plan(topic, platform, direction)
    else:
        base = build_final_pack(project, topic, language, platform, audience, direction)
        base["workflow"] = "Final Reel Pack Manifest"
    return base


def markdown_summary(package: dict[str, Any]) -> str:
    lines = [
        f"# Naz Lab Frontend Test Package: {package.get('workflow', '')}",
        "",
        f"Project: {package.get('project', '')}",
        f"Language: {package.get('language', '')}",
        f"Platform: {package.get('platform', '')}",
        f"Topic: {package.get('topic', '')}",
        "",
        "## Summary",
        "This package was generated from the Naz Lab Input Test Console.",
        "",
        "## JSON",
        "```json",
        pretty(package),
        "```",
    ]
    return "\n".join(lines)


def render_home() -> None:
    st.header("What this console does")
    st.success("Frontend input testing console for Naz Lab v1")
    st.markdown(
        """
Use this app when you want to test Naz Lab by typing input directly.

Main goal:

```text
Input topic -> Preview package -> Save JSON/Markdown -> Check result in Dashboard
```

This console is for frontend testing. It does not run heavy video generation.
"""
    )
    st.info("Video generation is deferred after v1. This console creates video plans/manifests only.")


def render_test_builder() -> None:
    st.header("Input test builder")
    st.caption("Type one topic and choose the workflow you want to test.")

    col1, col2, col3 = st.columns(3)
    with col1:
        project = st.selectbox("Project", PROJECTS, key="console_project")
        workflow = st.selectbox("Workflow to test", WORKFLOW_TYPES, key="console_workflow")
    with col2:
        language = st.selectbox("Language", LANGUAGES, index=0, key="console_language")
        platform = st.selectbox("Platform", PLATFORMS, key="console_platform")
    with col3:
        audience = st.text_input("Audience", value="Bangladeshi Facebook audience", key="console_audience")

    topic = st.text_area(
        "Main input / topic",
        height=160,
        value="বাংলাদেশে AI tools দিয়ে ছোট ব্যবসার content বানানো",
        key="console_topic",
    )
    direction = st.text_area(
        "Direction / style",
        height=100,
        value="সহজ বাংলা, practical tone, ৬০ সেকেন্ডের Reel-ready package",
        key="console_direction",
    )

    if not topic.strip():
        st.warning("Topic is required. Add a topic to preview and save a package.")
        return

    package = build_selected_package(project, workflow, topic, language, platform, audience, direction)
    json_text = pretty(package)
    md_text = markdown_summary(package)

    st.markdown("### Preview")
    preview_tabs = st.tabs(["Readable preview", "JSON", "Markdown"])
    with preview_tabs[0]:
        st.json(package)
    with preview_tabs[1]:
        st.text_area("Copy JSON", json_text, height=420, key="console_json_preview")
    with preview_tabs[2]:
        st.text_area("Copy Markdown", md_text, height=420, key="console_md_preview")

    folder, prefix = package_folder_for_workflow(workflow)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Save JSON package", key="console_save_json"):
            saved = save_json(folder, prefix, package)
            st.success(f"Saved JSON: {saved}")
    with c2:
        st.download_button("Download JSON", data=json_text, file_name=f"{prefix}_{now_stamp()}.json", mime="application/json")
    with c3:
        st.download_button("Download Markdown", data=md_text, file_name=f"{prefix}_{now_stamp()}.md", mime="text/markdown")

    st.caption(f"Default save folder: {folder}")


def render_quick_tests() -> None:
    st.header("Quick test checklist")
    st.markdown(
        """
Recommended order:

1. Full Content Package — save JSON.
2. Text / Script — check Bangla output.
3. Image Prompt — check prompt quality and safety.
4. Voice / TTS Plan — check generic, non-cloning voice package.
5. Portrait Prompt — check reference safety metadata.
6. Video Scene Plan — check planning only, no real generation.
7. Final Reel Pack Manifest — save frontend final pack.

After saving, open Dashboard -> Package Search or Final Packs to check saved outputs.
"""
    )


def render_launch() -> None:
    st.header("Launch")
    st.code("streamlit run test_console/app.py --server.port 8508 --server.address 0.0.0.0", language="bash")
    st.markdown("All-in-one launcher value:")
    st.code('WORKSTATION="test"', language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Input Test Console", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Input Test Console")
    st.caption("Phase 1.0 — frontend input testing for Naz Lab v1 workflows")
    ensure_dirs()
    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "test_console",
        {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")},
    )
    st.success("Input Test Console status: ready for frontend testing")
    st.info("Goal: type input, preview output, save package. Real video generation is deferred after v1.")

    tabs = st.tabs(["Home", "Input Builder", "Quick Tests", "Launch"])
    with tabs[0]:
        render_home()
    with tabs[1]:
        render_test_builder()
    with tabs[2]:
        render_quick_tests()
    with tabs[3]:
        render_launch()


if __name__ == "__main__":
    main()
