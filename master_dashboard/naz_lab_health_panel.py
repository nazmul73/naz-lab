"""Health and logs panel for Naz Lab Working Plan v2.0."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from shared.drive_paths import CONFIG_DIR, LOGS_DIR, REQUIRED_DIRECTORIES, REQUIRED_JSON_FILES, WORKSTATION_LINKS_JSON
from shared.job_queue_schema import read_json
from shared.model_policy import model_policy_status
from shared.ollama_persistence import ensure_ollama_persistence
from shared.ollama_text_generation import generation_policy_status


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def latest_logs(limit: int = 30) -> list[Path]:
    if not LOGS_DIR.exists():
        return []
    files = [item for item in LOGS_DIR.rglob("*") if item.is_file()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def safe_text(path: Path, limit: int = 10000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[-limit:]
    except Exception as exc:
        return f"Could not read log: {exc}"


def render_health_panel() -> None:
    st.subheader("Health/Logs")
    persistence = ensure_ollama_persistence()
    c1, c2, c3 = st.columns(3)
    c1.metric("Ollama persistence", "ok" if persistence.get("ok") else "check")
    c2.metric("Required folders", sum(1 for path in REQUIRED_DIRECTORIES if path.exists()))
    c3.metric("Log files", count_files(LOGS_DIR))

    st.markdown("### Backend policy")
    st.json({
        "generation_backend": "shared.ollama_text_generation.call_ollama",
        "helper_backend": "shared.text_workstation_helpers",
        "legacy_app_phase110_active": False,
        "ollama_persistence": persistence,
        "generation_policy": generation_policy_status(),
        "model_policy": model_policy_status(),
    })

    st.markdown("### Drive folder check")
    st.dataframe(
        [{"Path": str(path), "Status": "ready" if path.exists() else "missing", "Files": count_files(path)} for path in REQUIRED_DIRECTORIES],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Config files")
    st.json({str(path): read_json(path, {}) if path.exists() else "missing" for path in REQUIRED_JSON_FILES})
    st.markdown("### Workstation links")
    st.json(read_json(WORKSTATION_LINKS_JSON, {}))

    st.markdown("### Logs")
    logs = latest_logs()
    if not logs:
        st.info(f"No logs found in {LOGS_DIR}")
        return
    chosen = st.selectbox("Open log", [str(item) for item in logs], key="naz_health_log_select")
    st.text_area("Log tail", safe_text(Path(chosen)), height=320, key="naz_health_log_tail")
