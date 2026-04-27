"""Naz Lab Master Control Dashboard Phase 2.3."""

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
    IMAGE_PROMPTS,
    IMAGE_OUTPUTS,
    LOGS_DIR,
    OUTPUT_LOG_JSON,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import safe_read_json, update_workstation_status  # noqa: E402

PHASE = "2.3"
LANGUAGE_REQUIREMENT_EN = "Bangla and English output quality are primary requirements. Regional Bangla defaults to Rangpur/Nilphamari tone when requested. Other languages are optional."
LANGUAGE_REQUIREMENT_BN = "বাংলা হবে natural, fluent, Facebook-ready, voiceover-ready, netizen-style। আঞ্চলিক বাংলা চাইলে default হবে রংপুরিয়া/নীলফামারী tone। English হবে clean, practical, ready-to-use। অন্য ভাষা optional।"

BANGLA_STYLE_REQUIREMENTS = {
    "Primary regional Bangla": "রংপুরিয়া / উত্তরবঙ্গ / নীলফামারী tone হবে default regional flavor।",
    "Core Bangla": "স্বাভাবিক, সহজ, মুখে বলার মতো, ready-to-use বাংলা।",
    "Netizen Bangla": "Facebook comment/post/reel audience-এর মতো natural online tone।",
    "Voiceover Bangla": "মুখে পড়লে যেন কাঠখোট্টা না লাগে; short sentence, clear pacing।",
    "Secondary regional tones": "ঢাকাইয়া, চাটগাঁইয়া, সিলেটি, নোয়াখালী/কুমিল্লা tone থাকবে, কিন্তু user চাইলে ব্যবহার হবে।",
    "English": "Clean, practical, direct, ready-to-use English।",
}

FOLDERS = {
    "Chat outputs": CHAT_OUTPUTS,
    "Text outputs": TEXT_OUTPUTS,
    "Script outputs": SCRIPT_OUTPUTS,
    "Image prompts": IMAGE_PROMPTS,
    "Image outputs": IMAGE_OUTPUTS,
    "Image jobs": IMAGE_JOBS,
}

WORKSTATIONS = [
    {"name": "Text Workstation", "phase": "1.8 stable", "key": "text_workstation", "folder": TEXT_OUTPUTS},
    {"name": "Master Dashboard", "phase": "2.3 current", "key": "master_dashboard", "folder": BASE_PATH},
    {"name": "Image Workstation", "phase": "planned next", "key": "image_workstation", "folder": IMAGE_OUTPUTS},
    {"name": "Voice Workstation", "phase": "planned", "key": "voice_workstation", "folder": BASE_PATH / "voice_outputs"},
    {"name": "Video Workstation", "phase": "planned", "key": "video_workstation", "folder": BASE_PATH / "video_outputs"},
    {"name": "Portrait Workstation", "phase": "planned", "key": "portrait_workstation", "folder": BASE_PATH / "facefusion_outputs"},
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


def render_status(language: str) -> None:
    st.header("System status")
    links = read_json(WORKSTATION_LINKS_JSON, {})
    logs = output_log_entries()
    text_data = links.get("text_workstation", {}) if isinstance(links, dict) else {}
    text_status = text_data.get("status", "unknown")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dashboard phase", PHASE)
    c2.metric("Drive base", status_label(BASE_PATH))
    c3.metric("Text status", text_status)
    c4.metric("Output log entries", len(logs))

    st.info(LANGUAGE_REQUIREMENT_BN if language == "Bangla" else LANGUAGE_REQUIREMENT_EN)

    st.markdown("### Bangla and English quality requirements")
    st.json(BANGLA_STYLE_REQUIREMENTS)

    if text_data:
        st.markdown("### Text Workstation saved status")
        st.json(text_data)

    st.markdown("### Important paths")
    st.write({
        "base_path": str(BASE_PATH),
        "config_dir": str(CONFIG_DIR),
        "logs_dir": str(LOGS_DIR),
        "workstation_links_json": str(WORKSTATION_LINKS_JSON),
        "output_log_json": str(OUTPUT_LOG_JSON),
    })

    with st.expander("Latest output log events", expanded=False):
        if not logs:
            st.info("No log events yet.")
        else:
            st.dataframe(list(reversed(logs[-20:])), use_container_width=True, hide_index=True)


def render_workstations() -> None:
    st.header("Workstations")
    links = read_json(WORKSTATION_LINKS_JSON, {})
    rows = []
    for item in WORKSTATIONS:
        data = links.get(item["key"], {}) if isinstance(links, dict) else {}
        rows.append({
            "Workstation": item["name"],
            "Phase": item["phase"],
            "Status": data.get("status", "planned"),
            "Folder status": status_label(item["folder"]),
            "Files": count_files(item["folder"]),
            "Public URL": data.get("public_url", ""),
            "Last updated": data.get("last_updated", ""),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_outputs() -> None:
    st.header("Output folders")
    cols = st.columns(3)
    for index, (label, folder) in enumerate(FOLDERS.items()):
        with cols[index % 3]:
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
                if path.suffix.lower() in {".txt", ".md", ".json"}:
                    st.code(path.read_text(encoding="utf-8", errors="ignore")[:900])


def render_jobs() -> None:
    st.header("Job queue")
    jobs = latest_files(IMAGE_JOBS, limit=30, pattern="*.json")
    rows = []
    pending = 0
    completed = 0
    for path in jobs:
        data = read_json(path, {})
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        pending += 1 if status == "pending" else 0
        completed += 1 if status == "completed" else 0
        rows.append({
            "File": path.name,
            "Status": status,
            "Created": data.get("created_at", "") if isinstance(data, dict) else "",
            "Source": data.get("source_workstation", "") if isinstance(data, dict) else "",
            "Mode": data.get("source_mode", "") if isinstance(data, dict) else "",
        })

    c1, c2, c3 = st.columns(3)
    c1.metric("Image job files", len(jobs))
    c2.metric("Pending", pending)
    c3.metric("Completed", completed)

    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        selected = st.selectbox("Preview job", [row["File"] for row in rows])
        if selected:
            st.json(read_json(IMAGE_JOBS / selected, {}))
    else:
        st.info("No job files yet.")


def render_roadmap(language: str) -> None:
    st.header("Roadmap")
    if language == "Bangla":
        st.markdown(
            """
1. Phase 0 Foundation — complete  
2. Phase 1 Text Workstation — stable  
3. Phase 2 Master Control Dashboard — current  
4. Phase 3 Image Workstation — next  
5. Phase 4 Voice Workstation — planned  
6. Phase 5 Video Workstation — planned  
7. Phase 6 Portrait Workstation — planned

ভাষার priority:
- বাংলা: natural, fluent, netizen-style, voiceover-ready, ready-to-use হতে হবে।
- Primary আঞ্চলিক tone: রংপুরিয়া / উত্তরবঙ্গ / নীলফামারী flavor।
- Secondary regional support: ঢাকাইয়া, চাটগাঁইয়া, সিলেটি, নোয়াখালী/কুমিল্লা tone থাকবে, কিন্তু user চাইলে।
- English: clean, practical, ready-to-use হতে হবে।
- অন্য ভাষা: optional।
"""
        )
    else:
        st.markdown(
            """
1. Phase 0 Foundation — complete  
2. Phase 1 Text Workstation — stable  
3. Phase 2 Master Control Dashboard — current  
4. Phase 3 Image Workstation — next  
5. Phase 4 Voice Workstation — planned  
6. Phase 5 Video Workstation — planned  
7. Phase 6 Portrait Workstation — planned

Language priority:
- Bangla must be strong, natural, netizen-style, voiceover-ready, and ready to use.
- Primary regional Bangla tone: Rangpur / North Bengal / Nilphamari flavor.
- Secondary regional support: Dhakaiya, Chittagonian, Sylheti, Noakhali/Comilla tone when requested.
- English must be clean, practical, and ready to use.
- Other languages are optional.
"""
        )


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Control Dashboard")
    st.caption("Phase 2.3 Rangpur/Nilphamari-first Bangla dashboard")

    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "master_dashboard",
        {"status": "running", "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")},
    )

    with st.sidebar:
        st.header("Dashboard settings")
        language = st.radio("Dashboard language note", ["Bangla", "English"], index=0)
        st.caption("Primary Bangla regional default: Rangpur/Nilphamari. Secondary tones available when requested.")

    tab_status, tab_workstations, tab_outputs, tab_jobs, tab_roadmap = st.tabs([
        "Status", "Workstations", "Outputs", "Job Queue", "Roadmap"
    ])
    with tab_status:
        render_status(language)
    with tab_workstations:
        render_workstations()
    with tab_outputs:
        render_outputs()
    with tab_jobs:
        render_jobs()
    with tab_roadmap:
        render_roadmap(language)


if __name__ == "__main__":
    main()
