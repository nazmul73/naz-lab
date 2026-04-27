"""Naz Lab Video Workstation Phase 5.1.

Polished Bangla-first video package builder with hook, subtitles,
scene timing, editor instructions, project presets, and package workflow.
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

PHASE = "5.1"
VIDEO_OUTPUTS = BASE_PATH / "video_outputs"
VIDEO_PACKAGES = BASE_PATH / "video_packages"
VIDEO_STORYBOARDS = BASE_PATH / "video_storyboards"
VOICE_PACKAGES = BASE_PATH / "voice_packages"
IMAGE_JOBS = BASE_PATH / "image_jobs"
IMAGE_OUTPUTS = BASE_PATH / "image_outputs"

PROJECT_PRESETS = ["General", "True Noir Tales", "ToolFlow"]
CONTENT_TYPES = ["Reel video", "Facebook post video", "Carousel-to-video", "Story scene sequence", "Short explainer", "Ad-style short"]
LANGUAGE_OPTIONS = ["Bangla", "English", "Mixed Bangla-English"]
VIDEO_FORMATS = ["9:16 Reel/Shorts", "1:1 Square social", "4:5 Portrait post", "16:9 Wide", "Auto by context"]
VIDEO_LENGTHS = ["15 seconds", "30 seconds", "45 seconds", "60 seconds", "Custom"]
EDIT_STYLES = ["clean social edit", "cinematic suspense", "documentary reel", "creator explainer", "premium minimal", "fast tutorial", "slow emotional"]
SUBTITLE_STYLES = ["Bangla subtitles", "English subtitles", "Bilingual subtitles", "No subtitles", "Hook-only text"]
VISUAL_RHYTHMS = ["Hook-Context-Value-CTA", "Hook-Tension-Reveal-Question", "Problem-Solution-Steps-CTA", "Scene 1-Scene 2-Scene 3-CTA", "Narration-led"]
BROLL_TYPES = ["Auto by context", "Bangladeshi urban b-roll", "Rangpur/Nilphamari town", "workspace/dashboard", "AI tool screen", "street/documentary", "home/interior", "market/cafe", "cinematic human closeups"]
HOOK_STYLES = ["Question hook", "Shock hook", "Problem hook", "Story hook", "Benefit hook", "Curiosity hook"]
TIMING_STYLES = ["5-scene standard", "3-scene short", "6-scene detailed", "Narration-led timing", "Carousel-style timing"]
EDITOR_PLATFORMS = ["CapCut", "Premiere Pro", "DaVinci Resolve", "Mobile editor", "Generic editor"]
PACKAGE_STATUS = ["draft", "ready_for_edit", "video_generated", "blocked", "archived"]

PROJECT_DEFAULTS = {
    "General": {
        "language": "Bangla",
        "edit_style": "clean social edit",
        "subtitle_style": "Bangla subtitles",
        "rhythm": "Hook-Context-Value-CTA",
        "hook_style": "Question hook",
        "style": "Bangla-first general social video. Natural spoken Bangla, Facebook-ready, voiceover-ready, simple and human.",
    },
    "True Noir Tales": {
        "language": "English",
        "edit_style": "cinematic suspense",
        "subtitle_style": "English subtitles",
        "rhythm": "Hook-Tension-Reveal-Question",
        "hook_style": "Curiosity hook",
        "style": "English true crime/noir storytelling. Cinematic suspense, restrained emotion, adult-focused, no gore, no dead body, no visible wounds.",
    },
    "ToolFlow": {
        "language": "English",
        "edit_style": "creator explainer",
        "subtitle_style": "English subtitles",
        "rhythm": "Problem-Solution-Steps-CTA",
        "hook_style": "Problem hook",
        "style": "English AI tools / SaaS / productivity explainer. Clean, practical, premium, non-hype, workflow-focused.",
    },
}

CONTENT_RULES = {
    "Reel video": "Strong first 3 seconds, short scenes, subtitle-ready, mobile-first pacing.",
    "Facebook post video": "Readable pacing, clear subject, social-feed friendly composition.",
    "Carousel-to-video": "Each scene should map to a slide-like idea with clean transitions.",
    "Story scene sequence": "Narrative visual sequence with scene progression and emotional continuity.",
    "Short explainer": "Clear problem, practical solution, concise steps, direct CTA.",
    "Ad-style short": "Benefit-led, clean visuals, premium but not hype.",
}


def ensure_dirs() -> None:
    VIDEO_OUTPUTS.mkdir(parents=True, exist_ok=True)
    VIDEO_PACKAGES.mkdir(parents=True, exist_ok=True)
    VIDEO_STORYBOARDS.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "video"


def list_json_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.glob("*.json") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)


def list_video_files() -> list[Path]:
    if not VIDEO_OUTPUTS.exists():
        return []
    extensions = {".mp4", ".mov", ".webm", ".mkv"}
    return sorted([p for p in VIDEO_OUTPUTS.glob("*") if p.is_file() and p.suffix.lower() in extensions], key=lambda p: p.stat().st_mtime, reverse=True)


def suggested_video_filename(project: str, content_type: str) -> str:
    return f"{safe_name(project)}_{safe_name(content_type)}_{now_stamp()}.mp4"


def build_hook(project: str, language: str, hook_style: str, topic: str) -> str:
    source = topic.strip() or "এই বিষয়টা"
    if project == "True Noir Tales" or language == "English":
        if hook_style == "Question hook":
            return "What would you notice first?"
        if hook_style == "Shock hook":
            return "No one expected this detail to matter."
        if hook_style == "Problem hook":
            return "The problem was hiding in plain sight."
        if hook_style == "Benefit hook":
            return "This is the detail that changes the whole story."
        return "What looked normal at first was hiding something darker."
    if hook_style == "Question hook":
        return "তুমি হলে প্রথমে কোন জিনিসটা খেয়াল করতে?"
    if hook_style == "Shock hook":
        return "এই ছোট জিনিসটাই পুরো ব্যাপারটা বদলে দেয়।"
    if hook_style == "Problem hook":
        return "সমস্যাটা আসলে চোখের সামনেই ছিল।"
    if hook_style == "Benefit hook":
        return "এই সহজ পদ্ধতিটা তোমার সময় বাঁচাতে পারে।"
    if hook_style == "Story hook":
        return "ঘটনাটা শুরু হয়েছিল একদম সাধারণভাবে।"
    return f"{source} নিয়ে এই কথাটা অনেকেই খেয়াল করে না।"


def build_subtitle_lines(project: str, language: str, hook: str, topic: str) -> str:
    source = topic.strip() or "[মূল কথা এখানে বসবে]"
    if project == "ToolFlow" or language == "English":
        return (
            f"1. {hook}\n"
            "2. Random tools create random results.\n"
            "3. A simple workflow makes the output cleaner.\n"
            "4. Use the system, not just the tool.\n"
            "5. Would you try this?\n\n"
            f"Source: {source}"
        )
    if project == "True Noir Tales":
        return (
            f"1. {hook}\n"
            "2. The quiet detail matters most.\n"
            "3. The story changes when you notice it.\n"
            "4. Not everything is what it looks like.\n"
            "5. What would you have noticed first?\n\n"
            f"Source: {source}"
        )
    return (
        f"1. {hook}\n"
        "2. বিষয়টা সহজ, কিন্তু গুরুত্বপূর্ণ।\n"
        "3. এই জায়গাতেই অনেকের ভুল হয়।\n"
        "4. সহজভাবে দেখলে বিষয়টা পরিষ্কার।\n"
        "5. তোমার কী মনে হয়?\n\n"
        f"Source: {source}"
    )


def build_scene_sequence(topic: str, project: str, rhythm: str, length: str, hook: str, timing_style: str) -> str:
    source = topic.strip() or "[Paste topic/script here]"
    if timing_style == "3-scene short":
        timing = "Scene timing: 0-3s hook, 3-10s main point, 10-15s CTA."
    elif timing_style == "6-scene detailed":
        timing = "Scene timing: 0-3s hook, 3-8s context, 8-15s detail, 15-25s support, 25-35s result, final CTA."
    elif timing_style == "Carousel-style timing":
        timing = "Scene timing: each scene behaves like one carousel slide with one clear idea."
    else:
        timing = "Scene timing: 0-3s hook, 3-8s context, 8-15s main point, 15-25s support, final CTA."

    if project == "True Noir Tales":
        body = (
            f"Scene 1 - Hook: {hook}\n"
            "Scene 2 - Context: Establish the setting and emotional stakes.\n"
            "Scene 3 - Detail: Focus on the small clue or behavior that changes the meaning.\n"
            "Scene 4 - Tension: Slow zoom, darker mood, controlled narration beat.\n"
            "Scene 5 - Question CTA: End with a question that makes viewers comment."
        )
    elif project == "ToolFlow":
        body = (
            f"Scene 1 - Hook: {hook}\n"
            "Scene 2 - Problem: Show the messy workflow or wasted time.\n"
            "Scene 3 - System: Show the cleaner AI/SaaS workflow.\n"
            "Scene 4 - Result: Show the practical outcome or saved effort.\n"
            "Scene 5 - CTA: Ask whether the viewer would use the workflow."
        )
    else:
        body = (
            f"Scene 1 - Hook: {hook}\n"
            "Scene 2 - Context: Show the situation in a natural Bangladeshi setting.\n"
            "Scene 3 - Main point: Deliver the useful/emotional/story point.\n"
            "Scene 4 - Support: Add detail, example, or second visual.\n"
            "Scene 5 - CTA: End with a simple Bangla question or action line."
        )
    return f"{body}\n\n{timing}\nSource/topic: {source}\nTarget length: {length}\nRhythm: {rhythm}"


def build_video_direction(project: str, content_type: str, language: str, video_format: str, length: str, edit_style: str, subtitle_style: str, rhythm: str, broll_type: str, hook_style: str, timing_style: str, editor_platform: str, topic: str, custom_note: str) -> str:
    project_style = PROJECT_DEFAULTS[project]["style"]
    parts = [
        f"Project preset: {project}",
        f"Content type: {content_type}",
        f"Language: {language}",
        f"Video format: {video_format}",
        f"Target length: {length}",
        f"Edit style: {edit_style}",
        f"Subtitle style: {subtitle_style}",
        f"Visual rhythm: {rhythm}",
        f"B-roll type: {broll_type}",
        f"Hook style: {hook_style}",
        f"Timing style: {timing_style}",
        f"Editor platform: {editor_platform}",
        f"Project style: {project_style}",
        f"Content rule: {CONTENT_RULES.get(content_type, '')}",
        "Global language rule: Naz Lab is Bangla-first by default. Use English for True Noir Tales, ToolFlow, or when requested.",
        "Bangla rule: keep Bangla natural, spoken, Facebook-ready, netizen-friendly, and voiceover-ready.",
        "Regional rule: when useful, use Rangpur/Nilphamari/North Bengal flavor lightly and naturally.",
    ]
    if project == "True Noir Tales":
        parts.append("True Noir Tales video rules: adult-only, no gore, no dead body, no visible wounds, suspenseful but restrained, no sensational visual violence.")
    if project == "ToolFlow":
        parts.append("ToolFlow video rules: clean, practical, premium, non-hype, dashboard/workspace friendly, useful explainer flow.")
    if editor_platform == "CapCut":
        parts.append("CapCut editor note: use simple cuts, captions, subtle zooms, clean transitions, and avoid overusing effects.")
    if custom_note.strip():
        parts.append(f"Custom direction: {custom_note.strip()}")
    if topic.strip():
        parts.append(f"Source topic/script:\n{topic.strip()}")
    return "\n\n".join(parts)


def build_editor_instruction(scene_sequence: str, subtitle_lines: str, editor_platform: str, edit_style: str) -> str:
    return (
        f"Editor platform: {editor_platform}\n"
        f"Edit style: {edit_style}\n\n"
        "Editor instructions:\n"
        "1. Put the strongest hook in the first 3 seconds.\n"
        "2. Keep each scene visually clear and short.\n"
        "3. Match cuts to voiceover sentence breaks.\n"
        "4. Keep subtitles readable on mobile.\n"
        "5. Use clean transitions; avoid distracting effects.\n"
        "6. End with a clear question or CTA.\n\n"
        f"Scene sequence:\n{scene_sequence}\n\nSubtitle lines:\n{subtitle_lines}"
    )


def build_shot_list(scene_sequence: str, broll_type: str, subtitle_style: str) -> str:
    return (
        f"B-roll direction: {broll_type}\n"
        f"Subtitle direction: {subtitle_style}\n\n"
        "Shot list:\n"
        "1. Hook shot - strongest visual first.\n"
        "2. Context shot - establish setting.\n"
        "3. Detail shot - close-up/action/UI/detail.\n"
        "4. Support shot - second angle or proof visual.\n"
        "5. CTA shot - clean ending frame.\n\n"
        f"Scene sequence reference:\n{scene_sequence}"
    )


def build_package_json(project: str, content_type: str, language: str, status: str, suggested_output_path: str, video_direction: str, scene_sequence: str, shot_list: str, hook: str, subtitle_lines: str, editor_instruction: str) -> dict[str, Any]:
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "phase": PHASE,
        "project_preset": project,
        "content_type": content_type,
        "language": language,
        "status": status,
        "suggested_video_output_path": suggested_output_path,
        "hook": hook,
        "subtitle_lines": subtitle_lines,
        "video_direction": video_direction,
        "scene_sequence": scene_sequence,
        "shot_list": shot_list,
        "editor_instruction": editor_instruction,
        "future_backend": "placeholder",
    }


def save_package(package: dict[str, Any]) -> Path:
    ensure_dirs()
    path = VIDEO_PACKAGES / f"video_package_{safe_name(package['project_preset'])}_{now_stamp()}.json"
    safe_write_json(path, package)
    append_output_log(OUTPUT_LOG_JSON, workstation="video_workstation", event="video_package_saved", details={"path": str(path), "project": package["project_preset"], "status": package["status"]})
    return path


def save_storyboard(project: str, content: str) -> Path:
    ensure_dirs()
    path = VIDEO_STORYBOARDS / f"storyboard_{safe_name(project)}_{now_stamp()}.txt"
    path.write_text(content, encoding="utf-8")
    append_output_log(OUTPUT_LOG_JSON, workstation="video_workstation", event="video_storyboard_saved", details={"path": str(path), "project": project})
    return path


def render_status() -> None:
    st.header("Status")
    ensure_dirs()
    packages = list_json_files(VIDEO_PACKAGES)
    videos = list_video_files()
    storyboards = [p for p in VIDEO_STORYBOARDS.glob("*.txt") if p.is_file()] if VIDEO_STORYBOARDS.exists() else []
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Phase", PHASE)
    c2.metric("Video packages", len(packages))
    c3.metric("Storyboards", len(storyboards))
    c4.metric("Video files", len(videos))

    st.markdown("### Bangla-first rule")
    st.info("General video workflows default to Bangla. True Noir Tales and ToolFlow remain English-first presets unless changed.")

    st.markdown("### Project defaults")
    st.json(PROJECT_DEFAULTS)

    st.markdown("### Integration placeholders")
    st.write({
        "voice_packages": str(VOICE_PACKAGES),
        "image_jobs": str(IMAGE_JOBS),
        "image_outputs": str(IMAGE_OUTPUTS),
        "video_packages": str(VIDEO_PACKAGES),
        "video_outputs": str(VIDEO_OUTPUTS),
    })


def render_builder() -> None:
    st.header("Video package builder")
    project = st.selectbox("Project preset", PROJECT_PRESETS)
    defaults = PROJECT_DEFAULTS[project]
    content_type = st.selectbox("Content type", CONTENT_TYPES)
    language = st.selectbox("Language", LANGUAGE_OPTIONS, index=LANGUAGE_OPTIONS.index(defaults["language"]))
    video_format = st.selectbox("Video format", VIDEO_FORMATS)
    length = st.selectbox("Target length", VIDEO_LENGTHS, index=1)
    edit_style = st.selectbox("Edit style", EDIT_STYLES, index=EDIT_STYLES.index(defaults["edit_style"]))
    subtitle_style = st.selectbox("Subtitle style", SUBTITLE_STYLES, index=SUBTITLE_STYLES.index(defaults["subtitle_style"]))
    rhythm = st.selectbox("Visual rhythm", VISUAL_RHYTHMS, index=VISUAL_RHYTHMS.index(defaults["rhythm"]))
    broll_type = st.selectbox("B-roll type", BROLL_TYPES)
    hook_style = st.selectbox("Hook style", HOOK_STYLES, index=HOOK_STYLES.index(defaults["hook_style"]))
    timing_style = st.selectbox("Timing style", TIMING_STYLES)
    editor_platform = st.selectbox("Editor platform", EDITOR_PLATFORMS)
    package_status = st.selectbox("Package status", PACKAGE_STATUS)

    suggested_video = VIDEO_OUTPUTS / suggested_video_filename(project, content_type)
    st.text_input("Suggested future video output path", value=str(suggested_video))

    topic = st.text_area("Source topic/script", height=170, placeholder="Paste video topic, script, voice package summary, or image prompt idea here.")
    custom_note = st.text_area("Custom video direction", height=100, placeholder="Example: More cinematic, faster edit, stronger hook, more Bangla street realism, etc.")

    hook = build_hook(project, language, hook_style, topic)
    subtitle_lines = build_subtitle_lines(project, language, hook, topic)
    scene_sequence = build_scene_sequence(topic, project, rhythm, length, hook, timing_style)
    direction = build_video_direction(project, content_type, language, video_format, length, edit_style, subtitle_style, rhythm, broll_type, hook_style, timing_style, editor_platform, topic, custom_note)
    shot_list = build_shot_list(scene_sequence, broll_type, subtitle_style)
    editor_instruction = build_editor_instruction(scene_sequence, subtitle_lines, editor_platform, edit_style)
    combined = f"VIDEO DIRECTION:\n{direction}\n\nHOOK:\n{hook}\n\nSUBTITLE LINES:\n{subtitle_lines}\n\nSCENE SEQUENCE:\n{scene_sequence}\n\nSHOT LIST:\n{shot_list}\n\nEDITOR INSTRUCTION:\n{editor_instruction}"
    package = build_package_json(project, content_type, language, package_status, str(suggested_video), direction, scene_sequence, shot_list, hook, subtitle_lines, editor_instruction)

    st.markdown("### Hook")
    st.text_area("Video hook", hook, height=80)
    st.markdown("### Subtitle lines")
    st.text_area("Subtitle lines", subtitle_lines, height=180)
    st.markdown("### Copy-ready video direction")
    st.text_area("Video direction", direction, height=220)
    st.markdown("### Scene sequence")
    st.text_area("Scene sequence", scene_sequence, height=220)
    st.markdown("### Shot list")
    st.text_area("Shot list", shot_list, height=220)
    st.markdown("### Editor instruction")
    st.text_area("Editor instruction", editor_instruction, height=240)
    st.markdown("### Combined video package")
    st.text_area("Copy-ready combined package", combined, height=380)

    with st.expander("Video package JSON preview", expanded=False):
        st.json(package)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save storyboard"):
            path = save_storyboard(project, combined)
            st.success(f"Saved: {path}")
    with col2:
        if st.button("Save package JSON"):
            path = save_package(package)
            st.success(f"Saved: {path}")


def render_library() -> None:
    st.header("Video package library")
    ensure_dirs()
    packages = list_json_files(VIDEO_PACKAGES)
    storyboards = sorted([p for p in VIDEO_STORYBOARDS.glob("*.txt") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True) if VIDEO_STORYBOARDS.exists() else []

    st.metric("Package JSON files", len(packages))
    st.metric("Storyboard files", len(storyboards))

    if packages:
        selected_package = st.selectbox("Select package", [p.name for p in packages])
        st.json(safe_read_json(VIDEO_PACKAGES / selected_package, {}))

    if storyboards:
        selected_storyboard = st.selectbox("Select storyboard", [p.name for p in storyboards])
        path = VIDEO_STORYBOARDS / selected_storyboard
        st.text_area("Storyboard preview", path.read_text(encoding="utf-8", errors="ignore"), height=420)

    if not packages and not storyboards:
        st.info("No video packages saved yet.")


def render_inputs() -> None:
    st.header("Input package placeholders")
    st.markdown("Future versions will select image jobs, image outputs, and voice packages directly.")
    voice_packages = list_json_files(VOICE_PACKAGES)
    image_jobs = list_json_files(IMAGE_JOBS)
    st.write({
        "voice_package_count": len(voice_packages),
        "image_job_count": len(image_jobs),
        "image_outputs_path": str(IMAGE_OUTPUTS),
    })
    if voice_packages:
        selected_voice = st.selectbox("Preview voice package", [p.name for p in voice_packages])
        st.json(safe_read_json(VOICE_PACKAGES / selected_voice, {}))
    if image_jobs:
        selected_image_job = st.selectbox("Preview image job", [p.name for p in image_jobs])
        st.json(safe_read_json(IMAGE_JOBS / selected_image_job, {}))


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("Phase 5.1 builds polished video packages, hooks, subtitle lines, scene timing, and editor instructions. It does not generate video yet.")
    st.markdown("Future build: video backend integration and rendered video output library.")
    st.code("streamlit run video_workstation/app.py --server.port 8505 --server.address 0.0.0.0", language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Video Workstation", page_icon="🎬", layout="wide")
    st.title("🎬 Naz Lab Video Workstation")
    st.caption("Phase 5.1 — polished Bangla-first video package, hooks, subtitles, timing, editor instructions.")
    st.info("Naz Lab is Bangla-first by default. True Noir Tales and ToolFlow can stay English-first when selected.")
    ensure_dirs()
    update_workstation_status(WORKSTATION_LINKS_JSON, "video_workstation", {"status": "running", "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    tabs = st.tabs(["Status", "Builder", "Inputs", "Library", "Launch"])
    with tabs[0]:
        render_status()
    with tabs[1]:
        render_builder()
    with tabs[2]:
        render_inputs()
    with tabs[3]:
        render_library()
    with tabs[4]:
        render_launch()


if __name__ == "__main__":
    main()
