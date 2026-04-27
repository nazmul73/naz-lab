"""Naz Lab Master Control Dashboard Phase 2.0."""

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

PHASE = "2.0"
LANGUAGE_REQUIREMENT = "Bangla and English output quality are primary requirements. Other languages are optional."

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


def render_status() -> None:
    st.header("System status")
    links = read_json(WORKSTATION_LINKS_JSON, {})
    output_log = read_json(OUTPUT_LOG_JSON, [])
    text_status = links.get("text_workstation", {}).get("status", "unknown") if isinstance(links, dict) else "unknown"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dashboard phase", PHASE)
    c2.metric("Drive base", status_label(BASE_PATH))
    c3.metric("Text status", text_status)
    c4.metric("Output log entries", len(output_log) if isinstance(output_log, list) else 0)

    st.info(LANGUAGE_REQUIREMENT)
    st.write({
        "base_path": str(BASE_PATH),
        "config_dir": str(CONFIG_DIR),
        "logs_dir": str(LOGS_DIR),
        "workstation_links_json": str(WORKSTATION_LINKS_JSON),
        "output_log_json": str(OUTPUT_LOG_JSON),
    })


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
                    st.code(path.read_text(encoding="utf-8", errors="ignore")[:700])


def render_jobs() -> None:
    st.header("Job queue")
    jobs = latest_files(IMAGE_JOBS, limit=30, pattern="*.json")
    rows = []
    for path in jobs:
        data = read_json(path, {})
        rows.append({
            "File": path.name,
            "Status": data.get("status", "unknown") if isinstance(data, dict) else "unknown",
            "Created": data.get("created_at", "") if isinstance(data, dict) else "",
            "Source": data.get("source_workstation", "") if isinstance(data, dict) else "",
            "Mode": data.get("source_mode", "") if isinstance(data, dict) else "",
        })
    st.metric("Image job files", len(jobs))
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        selected = st.selectbox("Preview job", [row["File"] for row in rows])
        if selected:
            st.json(read_json(IMAGE_JOBS / selected, {}))
    else:
        st.info("No job files yet.")


def render_roadmap() -> None:
    st.header("Roadmap")
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
- Bangla: must be strong, natural, and ready to use.
- English: must be clean, practical, and ready to use.
- Other languages: optional.
"""
    )


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Control Dashboard")
    st.caption("Phase 2.0 foundation dashboard")

    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "master_dashboard",
        {"status": "running", "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")},
    )

    tab_status, tab_workstations, tab_outputs, tab_jobs, tab_roadmap = st.tabs([
        "Status", "Workstations", "Outputs", "Job Queue", "Roadmap"
    ])
    with tab_status:
        render_status()
    with tab_workstations:
        render_workstations()
    with tab_outputs:
        render_outputs()
    with tab_jobs:
        render_jobs()
    with tab_roadmap:
        render_roadmap()


if __name__ == "__main__":
    main()
