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
    if bangla:
        hook = "AI tool দিয়ে কাজ দ্রুত হয়, কিন্তু system ছাড়া output এলোমেলো হয়ে যায়।"
        problem = "অনেকে নতুন tool খোঁজে, কিন্তু একই কাজ repeat করার মতো workflow বানায় না।"
        solution_intro = "এই workflow-টা সেই জায়গাটাই ঠিক করে।"
        verdict = "Tool একা magic না। আসল লাভ আসে যখন tool, prompt আর process একসাথে কাজ করে।"
        cta = "তুমি কি এই workflowটা নিজের কাজে ব্যবহার করবে?"
        caption = "AI tool random ভাবে ব্যবহার না করে system বানালে কাজ অনেক পরিষ্কার হয়। তুমি কি এই setupটা try করবে?"
        steps = ["কাজের goal ঠিক করো", "একটা main tool বেছে নাও", "একই prompt/process repeat করো", "ভালো output save করে আবার ব্যবহার করো"]
        carousel_slides = ["AI tool নয়, system দরকার", "Problem: random tool use", "Solution: repeatable workflow", "Step 1: goal", "Step 2: tool", "Step 3: prompt/process", "Result: cleaner output", "CTA"]
    else:
        hook = "AI tools save time, but only when you use them as a system."
        problem = "Most people keep trying new tools without building a repeatable workflow."
        solution_intro = "This workflow turns the tool into a repeatable process."
        verdict = "The tool is not the advantage. The system you build around it is."
        cta = "Would you use this workflow?"
        caption = "AI tools work better when you stop using them randomly and start using them as a system. Would you try this setup?"
        steps = ["Define the goal", "Pick the main tool", "Use a repeatable prompt/process", "Save and reuse the best result"]
        carousel_slides = ["Stop using AI tools randomly", "The real problem", "The simple system", "Step 1: goal", "Step 2: tool", "Step 3: repeatable prompt", "Result: cleaner output", "CTA"]

    post = {
        "hook": hook,
        "problem": problem,
        "solution_intro": solution_intro,
        "topic_or_tool": topic,
        "steps": steps,
        "verdict": verdict,
        "cta": cta,
    }
    image_prompt = (
        "Clean modern SaaS/productivity visual, creator workstation or dashboard context, premium minimal composition, "
        "clear workflow feeling, practical and trustworthy mood, subtle AI/tool elements, no fake logos, no misleading UI, "
        "no clutter, no unreadable text, social-media-ready cover composition."
    )
    voice_direction = "Practical creator explainer voice, clear pacing, confident but non-hype, clean sentence breaks, useful and trustworthy delivery."
    if bangla:
        voice_direction += " Use natural spoken Bangla, simple, practical, beginner-friendly, and not stiff textbook Bangla."
    video_direction = (
        "5-scene explainer: Scene 1 messy/random workflow problem; Scene 2 simple system introduction; "
        "Scene 3 step-by-step workflow; Scene 4 result/benefit; Scene 5 CTA. Clean cuts, readable subtitles, minimal effects, no hype."
    )
    return {
        "main_post_package": post,
        "carousel_package": {"slides": carousel_slides, "note": "Each slide should use one clear idea and minimal text."},
        "reel_package": {"hook": hook, "target_length": "30 seconds", "cta": cta, "scene_sequence": ["Problem", "System", "Steps", "Result", "CTA"], "subtitle_note": "Use short mobile-readable subtitles."},
        "image_package": {"prompt": image_prompt, "format": "1:1, 4:5, or 9:16", "negative": "no fake logos, no misleading UI, no clutter, no unreadable text, no fake income claim"},
        "voice_package": {"direction": voice_direction, "language": language, "reference_policy": REFERENCE_POLICY},
        "video_package": {"direction": video_direction, "platform": platform},
        "posting_package": {"caption": caption, "cta": cta, "hashtags": ["#AITools", "#Productivity", "#Automation", "#SaaS", "#Workflow", "#ToolFlow", "#NoCode"]},
        "safety_notes": ["no fake income claims", "no spammy marketer tone", "no misleading product UI", "no unverified AI news"],
        "notes": note,
        "audience": audience,
    }


def build_general_package(topic: str, language: str, platform: str, audience: str, note: str) -> dict[str, Any]:
    bangla = language in {"Bangla", "Mixed Bangla-English"}
    if bangla:
        title = "একটা সহজ কথা, কিন্তু কাজে লাগে"
        hook = "এই কথাটা অনেকেই খেয়াল করে না।"
        body = f"{topic}\n\nব্যাপারটা বাইরে থেকে ছোট মনে হলেও, ঠিকভাবে ব্যবহার করলে এটা content, কাজ, বা daily decision—সব জায়গায় কাজে লাগতে পারে।"
        value_line = "সবচেয়ে ভালো ফল আসে যখন কথাটা সহজ রাখা হয়, কিন্তু কাজে লাগার মতো করে সাজানো হয়।"
        cta = "তোমার কী মনে হয়?"
        caption = "সহজ জিনিস ঠিকভাবে ব্যবহার করলেই অনেক সময় সবচেয়ে ভালো result আসে। তোমার কী মনে হয়?"
        reel_script = {
            "hook": hook,
            "voiceover": [
                hook,
                "আমরা অনেক সময় বড় solution খুঁজি।",
                "কিন্তু ছোট একটা idea ঠিকভাবে সাজাতে পারলেই কাজ অনেক সহজ হয়।",
                value_line,
                cta,
            ],
            "on_screen_text": ["ছোট idea", "সঠিকভাবে সাজাও", "কাজে লাগাও", "তোমার কী মনে হয়?"],
        }
        regional_note = "Default light regional flavor: Rangpur/Nilphamari/North Bengal. Keep it natural, not exaggerated."
    else:
        title = "A simple idea that actually helps"
        hook = "Most people miss this simple point."
        body = f"{topic}\n\nIt may look small from the outside, but when you structure it clearly, it can help with content, work, or daily decisions."
        value_line = "The best results usually come from keeping the idea simple and making it useful."
        cta = "What do you think?"
        caption = "Simple ideas often work best when they are structured clearly. What do you think?"
        reel_script = {
            "hook": hook,
            "voiceover": [hook, "We often look for big solutions.", "But a small idea can become useful when it is structured clearly.", value_line, cta],
            "on_screen_text": ["Small idea", "Structure it", "Use it", "What do you think?"],
        }
        regional_note = "English mode selected. Bangla-first remains the global default for Naz Lab."

    image_prompt = (
        "Natural Bangladeshi social content visual, realistic human-centered scene, culturally grounded, "
        "urban or rural Bangladesh as appropriate, everyday believable environment, warm natural expression, "
        "premium Facebook-ready composition, no misleading elements, no fake logos, no sindoor unless explicitly requested."
    )
    voice_direction = "Natural spoken Bangla, Facebook-ready, voiceover-ready, clear pauses, one idea per sentence, simple and human delivery."
    if not bangla:
        voice_direction = "Natural clear social-media voice, simple phrasing, useful tone, no hype."
    video_direction = "Hook-context-value-CTA video package, subtitle-friendly lines, short mobile-readable captions, simple cuts, clean final CTA frame."

    return {
        "text_package": {"title": title, "hook": hook, "body": body, "value_line": value_line, "cta": cta, "bangla_rule": BANGLA_RULE},
        "reel_package": {"target_length": "30-45 seconds", "script": reel_script, "scene_sequence": ["Hook", "Problem/context", "Simple idea", "Value", "CTA"]},
        "image_package": {"prompt": image_prompt, "format": "1:1, 4:5, or 9:16", "negative": "no fake logo, no misleading elements, no clutter, no sindoor unless requested"},
        "voice_package": {"direction": voice_direction, "language": language, "reference_policy": REFERENCE_POLICY},
        "video_package": {"direction": video_direction, "platform": platform, "subtitle_note": "Keep Bangla subtitles short, mobile-readable, and matched to voice pauses."},
        "posting_package": {"caption": caption, "cta": cta, "hashtags": ["#BanglaContent", "#FacebookContent", "#SocialMediaContent"]},
        "regional_note": regional_note,
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
