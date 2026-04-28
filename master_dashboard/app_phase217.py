"""Naz Lab Master Dashboard Phase 2.17.

Focused dashboard for backend/frontend items 8-10:
- queue visibility
- text output browser
- image job browser

No heavy generation runs from this dashboard.
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

from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    CHAT_OUTPUTS,
    IMAGE_JOBS,
    IMAGE_PROMPTS,
    OUTPUT_LOG_JSON,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.job_queue_schema import summarize_job_file, validate_job_record  # noqa: E402
from shared.json_utils import safe_read_json, update_workstation_status  # noqa: E402

PHASE = "2.17"
PHASE_STATUS = "queue-text-image-visibility-ready"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


def latest_files(folder: Path, pattern: str = "*", limit: int = 200) -> list[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.rglob(pattern) if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def file_row(path: Path) -> dict[str, str]:
    return {
        "File": path.name,
        "Folder": path.parent.name,
        "Modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "Path": str(path),
    }


def render_status() -> None:
    st.header("Backend / Frontend Status")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dashboard phase", PHASE)
    c2.metric("Text outputs", len(latest_files(TEXT_OUTPUTS, "*.txt", 1000)))
    c3.metric("Script outputs", len(latest_files(SCRIPT_OUTPUTS, "*.txt", 1000)))
    c4.metric("Image jobs", len(latest_files(IMAGE_JOBS, "*.json", 1000)))
    st.success("Queue visibility, Text Output browser, and Image Job browser are connected.")
    st.info("Real image/video generation remains outside this dashboard. This panel only monitors and previews saved files/jobs.")
    links = safe_read_json(WORKSTATION_LINKS_JSON, {})
    st.json({"phase": PHASE, "status": PHASE_STATUS, "base_path": str(BASE_PATH), "workstation_links": links})


def render_text_outputs() -> None:
    st.header("Text Output Browser")
    folders = {
        "All text-like outputs": [TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS, CHAT_OUTPUTS],
        "Text outputs": [TEXT_OUTPUTS],
        "Script outputs": [SCRIPT_OUTPUTS],
        "Image prompts": [IMAGE_PROMPTS],
        "Chat outputs": [CHAT_OUTPUTS],
    }
    label = st.selectbox("Folder", list(folders.keys()))
    keyword = st.text_input("Search text", value="")
    files: list[Path] = []
    for folder in folders[label]:
        files.extend(latest_files(folder, "*.txt", 500))
    files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
    if keyword:
        files = [p for p in files if keyword.lower() in p.name.lower() or keyword.lower() in read_text(p).lower()]
    st.metric("Matching files", len(files))
    if not files:
        st.info("No matching text outputs found.")
        return
    rows = [file_row(path) for path in files]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open output", [row["Path"] for row in rows]))
    content = read_text(selected)
    st.download_button("Download selected TXT", data=content, file_name=selected.name, mime="text/plain")
    st.text_area("Preview", content, height=480)


def render_image_jobs() -> None:
    st.header("Image Job Browser")
    jobs = latest_files(IMAGE_JOBS, "*.json", 1000)
    rows = [summarize_job_file(path) for path in jobs]
    status_filter = st.selectbox("Status", ["all", "created", "queued", "processing", "done", "failed", "approved", "rejected"], index=0)
    review_filter = st.selectbox("Review", ["all", "pending", "approved", "rejected"], index=0)
    keyword = st.text_input("Search jobs", value="")
    if status_filter != "all":
        rows = [r for r in rows if r.get("Status") == status_filter]
    if review_filter != "all":
        rows = [r for r in rows if r.get("Review") == review_filter]
    if keyword:
        q = keyword.lower()
        rows = [r for r in rows if q in json.dumps(r, ensure_ascii=False).lower()]
    c1, c2, c3 = st.columns(3)
    c1.metric("Matching jobs", len(rows))
    c2.metric("Valid jobs", sum(1 for r in rows if r.get("Valid")))
    c3.metric("Invalid jobs", sum(1 for r in rows if not r.get("Valid")))
    if not rows:
        st.info("No matching image jobs found.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open image job JSON", [row["Path"] for row in rows]))
    data = read_json(selected)
    ok, messages = validate_job_record(data)
    if ok:
        st.success("Job JSON validates against Phase 1.10 queue schema.")
    else:
        st.warning("Job JSON has schema warnings: " + "; ".join(messages))
    text = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button("Download selected JSON", data=text, file_name=selected.name, mime="application/json")
    st.json(data)
    st.text_area("Copy JSON", text, height=420)


def render_queue_visibility() -> None:
    st.header("Queue Visibility")
    job_files = latest_files(IMAGE_JOBS, "*.json", 2000)
    rows = [summarize_job_file(path) for path in job_files]
    grouped: dict[str, int] = {}
    for row in rows:
        grouped[row.get("Status", "unknown")] = grouped.get(row.get("Status", "unknown"), 0) + 1
    st.json({"image_jobs_by_status": grouped, "total_image_jobs": len(rows), "queue_folder": str(IMAGE_JOBS)})
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No image queue jobs found yet.")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Dashboard")
    st.caption("Phase 2.17 — queue visibility, text output browser, image job browser")
    tabs = st.tabs(["Status", "Queue Visibility", "Text Outputs", "Image Jobs"])
    with tabs[0]:
        render_status()
    with tabs[1]:
        render_queue_visibility()
    with tabs[2]:
        render_text_outputs()
    with tabs[3]:
        render_image_jobs()


if __name__ == "__main__":
    main()
