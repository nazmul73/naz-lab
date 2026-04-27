"""Naz Lab Master Control Dashboard Phase 2.9 stable stack refresh."""

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

from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    CHAT_OUTPUTS,
    CONFIG_DIR,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    IMAGE_PROMPTS,
    LOGS_DIR,
    OUTPUT_LOG_JSON,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import safe_read_json, update_workstation_status  # noqa: E402

PHASE = "2.9"
PHASE_STATUS = "stable"

VOICE_OUTPUTS = BASE_PATH / "voice_outputs"
VOICE_PACKAGES = BASE_PATH / "voice_packages"
VOICE_REFERENCES = BASE_PATH / "voice_references"
VOICE_PROFILE_PACKAGES = BASE_PATH / "voice_profile_packages"
AUDIO_OUTPUTS = BASE_PATH / "audio_outputs"
VIDEO_OUTPUTS = BASE_PATH / "video_outputs"
VIDEO_PACKAGES = BASE_PATH / "video_packages"
VIDEO_STORYBOARDS = BASE_PATH / "video_storyboards"
PORTRAIT_PACKAGES = BASE_PATH / "portrait_packages"
PORTRAIT_OUTPUTS = BASE_PATH / "portrait_outputs"
PORTRAIT_REFERENCES = BASE_PATH / "portrait_references"
PROJECT_PACKAGES = BASE_PATH / "project_packages"
PROJECT_WORKFLOWS = BASE_PATH / "project_workflows"

LANGUAGE_REQUIREMENT_EN = "Naz Lab is Bangla-first by default. English is second and remains default for True Noir Tales / ToolFlow when selected. Other languages are optional."
LANGUAGE_REQUIREMENT_BN = "Naz Lab default হবে Bangla-first। বেশির ভাগ content বাংলায় হবে। English থাকবে selected English project বা user request অনুযায়ী। আঞ্চলিক বাংলা লাগলে primary default: রংপুর/নীলফামারী/উত্তরবঙ্গ।"

BANGLA_STYLE_REQUIREMENTS = {
    "Global priority": "Bangla first, English second, other languages optional.",
    "Core Bangla": "স্বাভাবিক, সহজ, মুখে বলার মতো, ready-to-use বাংলা।",
    "Netizen Bangla": "Facebook comment/post/reel audience-এর মতো natural online tone।",
    "Voiceover Bangla": "মুখে পড়লে যেন কাঠখোট্টা না লাগে; short sentence, clear pacing।",
    "Primary regional Bangla": "রংপুরিয়া / উত্তরবঙ্গ / নীলফামারী tone হবে default regional flavor।",
    "Secondary regional tones": "ঢাকাইয়া, চাটগাঁইয়া, সিলেটি, নোয়াখালী/কুমিল্লা tone user চাইলে থাকবে।",
    "English exceptions": "True Noir Tales and ToolFlow can stay English-first when selected.",
}

PROJECT_AUTOMATION_STATUS = {
    "True Noir Tales": "polished one-topic-to-full-package automation",
    "ToolFlow": "polished one-topic-to-full-package automation",
    "General Bangla": "polished Bangla-first one-topic-to-full-package automation",
}

FOLDERS = {
    "Chat outputs": CHAT_OUTPUTS,
    "Text outputs": TEXT_OUTPUTS,
    "Script outputs": SCRIPT_OUTPUTS,
    "Image prompts": IMAGE_PROMPTS,
    "Image jobs": IMAGE_JOBS,
    "Image outputs": IMAGE_OUTPUTS,
    "Voice outputs": VOICE_OUTPUTS,
    "Voice packages": VOICE_PACKAGES,
    "Voice reference audio": VOICE_REFERENCES,
    "Voice profile packages": VOICE_PROFILE_PACKAGES,
    "Audio outputs": AUDIO_OUTPUTS,
    "Video outputs": VIDEO_OUTPUTS,
    "Video packages": VIDEO_PACKAGES,
    "Video storyboards": VIDEO_STORYBOARDS,
    "Portrait packages": PORTRAIT_PACKAGES,
    "Portrait outputs": PORTRAIT_OUTPUTS,
    "Portrait references": PORTRAIT_REFERENCES,
    "Project packages": PROJECT_PACKAGES,
    "Project workflows": PROJECT_WORKFLOWS,
}

WORKSTATIONS = [
    {"name": "Text Workstation", "phase": "1.8 stable", "key": "text_workstation", "folder": TEXT_OUTPUTS, "port": "8501"},
    {"name": "Master Dashboard", "phase": "2.9 stable", "key": "master_dashboard", "folder": BASE_PATH, "port": "8502"},
    {"name": "Image Workstation", "phase": "3.x stable", "key": "image_workstation", "folder": IMAGE_OUTPUTS, "port": "8503"},
    {"name": "Voice Workstation", "phase": "4.x reference workflow", "key": "voice_workstation", "folder": VOICE_OUTPUTS, "port": "8504"},
    {"name": "Video Workstation", "phase": "5.3 stable", "key": "video_workstation", "folder": VIDEO_OUTPUTS, "port": "8505"},
    {"name": "Portrait Workstation", "phase": "6.3 stable", "key": "portrait_workstation", "folder": PORTRAIT_PACKAGES, "port": "8506"},
    {"name": "Project Workflow Workstation", "phase": "10.2 stable", "key": "project_workstation", "folder": PROJECT_PACKAGES, "port": "8507"},
]


def read_json(path: Path, default: Any) -> Any:
    try:
        return safe_read_json(path, default)
    except Exception:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default


def output_log_entries() -> list[dict[str, Any]]:
    data = read_json(OUTPUT_LOG_JSON, {"logs": []})
    if isinstance(data, dict) and isinstance(data.get("logs"), list):
        return data["logs"]
    if isinstance(data, list):
        return data
    return []


def count_files(folder: Path, pattern: str = "*") -> int:
    if not folder.exists():
        return 0
    return sum(1 for item in folder.glob(pattern) if item.is_file())


def latest_files(folder: Path, limit: int = 5, pattern: str = "*") -> list[Path]:
    if not folder.exists():
        return []
    files = [item for item in folder.glob(pattern) if item.is_file()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def status_label(folder: Path) -> str:
    return "OK" if folder.exists() and folder.is_dir() else "Missing"


def workstation_data() -> dict[str, Any]:
    data = read_json(WORKSTATION_LINKS_JSON, {})
    return data if isinstance(data, dict) else {}


def link_markdown(label: str, url: str) -> None:
    if url:
        st.markdown(f"[{label}]({url})")
    else:
        st.caption("No URL saved yet. Save it from the Links tab.")


def render_status(language: str) -> None:
    st.header("System status")
    links = workstation_data()
    logs = output_log_entries()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Dashboard phase", PHASE)
    c2.metric("Dashboard status", PHASE_STATUS)
    c3.metric("Drive base", status_label(BASE_PATH))
    c4.metric("Active workstations", str(len(WORKSTATIONS)))
    c5.metric("Output log entries", len(logs))
    st.success("Master Dashboard status: stable for Phase 2.9 full stack refresh")
    st.info(LANGUAGE_REQUIREMENT_BN if language == "Bangla" else LANGUAGE_REQUIREMENT_EN)

    st.markdown("### Workstation matrix")
    rows = []
    for item in WORKSTATIONS:
        data = links.get(item["key"], {})
        rows.append({
            "Workstation": item["name"],
            "Phase": item["phase"],
            "Saved status": data.get("status", "planned"),
            "Folder": status_label(item["folder"]),
            "Files": count_files(item["folder"]),
            "Port": item["port"],
            "URL saved": "yes" if data.get("public_url") else "no",
            "Last seen": data.get("last_seen", ""),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("### Project automation status")
    st.json(PROJECT_AUTOMATION_STATUS)

    st.markdown("### Quick links")
    cols = st.columns(4)
    for index, item in enumerate(WORKSTATIONS):
        with cols[index % 4]:
            st.markdown(f"**{item['name']}**")
            link_markdown("Open", links.get(item["key"], {}).get("public_url", ""))

    st.markdown("### Next readiness")
    st.write({
        "current_stack": "Text + Dashboard + Image + Voice + Video + Portrait + Project Workflow",
        "project_automation": "True Noir Tales + ToolFlow + General Bangla polished",
        "recommended_next_1": "Dashboard reporting and package search/filter",
        "recommended_next_2": "Safer reference managers where needed",
        "recommended_next_3": "Optional backend planning",
        "status": "ready",
    })
    st.markdown("### Bangla-first quality requirements")
    st.json(BANGLA_STYLE_REQUIREMENTS)


def render_links() -> None:
    st.header("Links")
    st.caption("Save current Cloudflare URLs so the dashboard can show quick open links.")
    links = workstation_data()
    with st.form("save_links_form"):
        values = {}
        for item in WORKSTATIONS:
            data = links.get(item["key"], {})
            values[item["key"]] = st.text_input(f"{item['name']} public URL", value=data.get("public_url", ""))
        submitted = st.form_submit_button("Save URLs")
    if submitted:
        for item in WORKSTATIONS:
            url = values[item["key"]].strip()
            if url:
                update_workstation_status(WORKSTATION_LINKS_JSON, item["key"], {"public_url": url, "status": "stable", "phase": item["phase"]})
        st.success("URLs saved to workstation_links.json")
        st.rerun()


def render_workstations() -> None:
    st.header("Workstations")
    links = workstation_data()
    rows = []
    for item in WORKSTATIONS:
        data = links.get(item["key"], {})
        rows.append({
            "Workstation": item["name"],
            "Phase": item["phase"],
            "Status": data.get("status", "planned"),
            "Folder status": status_label(item["folder"]),
            "Files": count_files(item["folder"]),
            "Public URL": data.get("public_url", ""),
            "Last updated": data.get("last_updated", data.get("last_seen", "")),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_outputs() -> None:
    st.header("Output folders")
    cols = st.columns(4)
    for index, (label, folder) in enumerate(FOLDERS.items()):
        with cols[index % 4]:
            st.metric(label, count_files(folder))
            st.caption(str(folder))
    st.markdown("### Latest files")
    for label, folder in FOLDERS.items():
        with st.expander(label, expanded=False):
            files = latest_files(folder, limit=5)
            if not files:
                st.info("No files yet.")
                continue
            for path in files:
                modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(f"**{path.name}** — {modified}")


def render_jobs() -> None:
    st.header("Job queue")
    sections = {
        "Image jobs": IMAGE_JOBS,
        "Voice packages": VOICE_PACKAGES,
        "Voice profile packages": VOICE_PROFILE_PACKAGES,
        "Video packages": VIDEO_PACKAGES,
        "Portrait packages": PORTRAIT_PACKAGES,
        "Project packages": PROJECT_PACKAGES,
    }
    for label, folder in sections.items():
        st.markdown(f"### {label}")
        files = latest_files(folder, limit=30, pattern="*.json")
        rows = []
        for path in files:
            data = read_json(path, {})
            rows.append({
                "File": path.name,
                "Status": data.get("status", "unknown") if isinstance(data, dict) else "unknown",
                "Project": data.get("project_preset", data.get("visual_preset", "")) if isinstance(data, dict) else "",
                "Content": data.get("content_type", data.get("portrait_type", data.get("platform", ""))) if isinstance(data, dict) else "",
                "Created": data.get("created_at", "") if isinstance(data, dict) else "",
            })
        st.metric(f"{label} count", len(files))
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info(f"No {label.lower()} yet.")


def render_launch() -> None:
    st.header("Launch instructions")
    st.write({
        "Text Workstation": "8501",
        "Master Dashboard": "8502",
        "Image Workstation": "8503",
        "Voice Workstation": "8504",
        "Video Workstation": "8505",
        "Portrait Workstation": "8506",
        "Project Workflow Workstation": "8507",
    })
    st.markdown("Recommended: use `launchers/all_in_one_colab_launcher.md` and set `WORKSTATION` to the app you want.")
    st.code('WORKSTATION="project"', language="bash")
    st.code("streamlit run project_workstation/app.py --server.port 8507 --server.address 0.0.0.0", language="bash")


def render_roadmap(language: str) -> None:
    st.header("Roadmap")
    st.markdown("""
1. Phase 0 Foundation — complete  
2. Phase 1 Text Workstation — stable  
3. Phase 2 Master Dashboard — stable full stack refresh  
4. Phase 3 Image Workstation — stable  
5. Phase 4 Voice Workstation — reference workflow active  
6. Phase 5 Video Workstation — stable  
7. Phase 6 Portrait Workstation — stable  
8. Phase 7 All-in-one Launcher — ready  
9. Phase 8 True Noir Tales / ToolFlow workflow docs — ready  
10. Phase 9 Bangla Quality Engine — active  
11. Phase 10 Project Workflow Workstation — stable and polished
""")
    st.markdown("### Project automation")
    st.json(PROJECT_AUTOMATION_STATUS)
    if language == "Bangla":
        st.markdown("""
পরের কাজের priority:
- Dashboard reporting এবং package search/filter উন্নত করা
- দরকার হলে safer reference manager যোগ করা
- backend planning শুরু করা
- Bangla quality engine সব জায়গায় aligned রাখা
""")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Control Dashboard")
    st.caption("Phase 2.9 refresh — full stack plus polished Project Workflow automation")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    with st.sidebar:
        st.header("Dashboard settings")
        language = st.radio("Dashboard language note", ["Bangla", "English"], index=0)
        st.caption("Naz Lab default: Bangla-first. Regional default: Rangpur/Nilphamari/North Bengal.")
        st.success("Phase 2.9 stable")
    tabs = st.tabs(["Status", "Links", "Workstations", "Outputs", "Job Queue", "Launch", "Roadmap"])
    with tabs[0]: render_status(language)
    with tabs[1]: render_links()
    with tabs[2]: render_workstations()
    with tabs[3]: render_outputs()
    with tabs[4]: render_jobs()
    with tabs[5]: render_launch()
    with tabs[6]: render_roadmap(language)


if __name__ == "__main__":
    main()
