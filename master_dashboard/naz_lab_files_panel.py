"""Files panel for Naz Lab Working Plan v2.0."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from shared.drive_paths import BASE_PATH, CHAT_OUTPUTS, CONFIG_DIR, IMAGE_JOBS, IMAGE_OUTPUTS, LOGS_DIR, TEXT_METADATA, TEXT_OUTPUTS, VIDEO_JOBS, VIDEO_OUTPUTS, VOICE_JOBS, VOICE_OUTPUTS
from shared.job_queue_schema import read_json

TEXT_EXTENSIONS = {".txt", ".md", ".json", ".jsonl", ".log"}


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def latest_files(path: Path, limit: int = 40) -> list[Path]:
    if not path.exists():
        return []
    files = [item for item in path.rglob("*") if item.is_file()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def safe_text(path: Path, limit: int = 8000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception as exc:
        return f"Could not read file: {exc}"


def render_files_panel() -> None:
    st.subheader("Files")
    areas = {
        "Base": BASE_PATH,
        "Text outputs": TEXT_OUTPUTS,
        "Chat outputs": CHAT_OUTPUTS,
        "Text metadata": TEXT_METADATA,
        "Image jobs": IMAGE_JOBS,
        "Image outputs": IMAGE_OUTPUTS,
        "Voice jobs": VOICE_JOBS,
        "Voice outputs": VOICE_OUTPUTS,
        "Video jobs": VIDEO_JOBS,
        "Video outputs": VIDEO_OUTPUTS,
        "Config": CONFIG_DIR,
        "Logs": LOGS_DIR,
    }
    st.dataframe(
        [{"Area": name, "Path": str(path), "Files": count_files(path), "Status": "ready" if path.exists() else "missing"} for name, path in areas.items()],
        use_container_width=True,
        hide_index=True,
    )
    selected = st.selectbox("Browse area", list(areas.keys()), key="naz_files_area")
    folder = areas[selected]
    files = latest_files(folder)
    if not files:
        st.info(f"No files found in {folder}")
        return
    rows = [{"Name": item.name, "Path": str(item), "Size KB": round(item.stat().st_size / 1024, 1)} for item in files]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    chosen = st.selectbox("Inspect", [str(item) for item in files], key="naz_files_inspect")
    path = Path(chosen)
    if path.suffix.lower() == ".json":
        st.json(read_json(path, {}))
    elif path.suffix.lower() in TEXT_EXTENSIONS:
        st.text_area("Content", safe_text(path), height=300, key="naz_files_content")
    else:
        st.info("Text preview is limited to text, json, jsonl, md, and log files.")
