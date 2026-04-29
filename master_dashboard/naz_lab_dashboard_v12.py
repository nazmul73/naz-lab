"""Naz Lab dashboard v1.6.

Single app command center with Text, Voice job workflow, Image, contextual
Review Package, and Facebook Post controls merged. No tab named Complete
Package is used.
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

from master_dashboard.naz_lab_facebook_panel import render_facebook_panel  # noqa: E402
from master_dashboard.naz_lab_image_panel import render_image_panel  # noqa: E402
from master_dashboard.naz_lab_review_panel import render_review_panel  # noqa: E402
from master_dashboard.naz_lab_text_panel import render_text_panel  # noqa: E402
from master_dashboard.naz_lab_voice_panel import render_voice_panel  # noqa: E402
from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    CONFIG_DIR,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    LOGS_DIR,
    VIDEO_JOBS,
    VIDEO_OUTPUTS,
    VOICE_JOBS,
    VOICE_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.job_queue_schema import read_json  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402

PHASE = "naz-lab-dashboard-1.6"
STATUS = "text-voice-image-review-facebook-workflows-merged"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
JSON_EXTENSIONS = {".json"}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def latest_files(path: Path, extensions: set[str] | None = None, limit: int = 12) -> list[Path]:
    if not path.exists():
        return []
    files = [item for item in path.rglob("*") if item.is_file()]
    if extensions:
        files = [item for item in files if item.suffix.lower() in extensions]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def safe_json(path: Path, default: Any) -> Any:
    try:
        return read_json(path, default)
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}


def file_rows(path: Path, extensions: set[str] | None = None, limit: int = 30) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in latest_files(path, extensions=extensions, limit=limit):
        rows.append({"Name": item.name, "Path": str(item), "Size KB": round(item.stat().st_size / 1024, 1)})
    return rows


def render_css() -> None:
    st.markdown(
        """
        <style>
          .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
          .naz-hero {padding: 1.4rem 1.5rem; border-radius: 26px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%); color: white; margin-bottom: 1rem; box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);}
          .naz-hero h1 {margin:0; font-size:2.35rem; letter-spacing: -0.04em;}
          .naz-hero p {margin:0.45rem 0 0 0; opacity:0.92; font-size:1.04rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    update_workstation_status(WORKSTATION_LINKS_JSON, "naz_lab", {"status": STATUS, "phase": PHASE, "last_seen": now_iso()})
    st.markdown(
        """
        <div class="naz-hero">
          <h1>Naz Lab</h1>
          <p>Unified AI workstation command center for text, voice, image, video planning, Facebook handoff, review packages, files, and system health.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_strip() -> None:
    cols = st.columns(6)
    cols[0].metric("Text", "MERGED")
    cols[1].metric("Voice", "JOB READY")
    cols[2].metric("Image", "MERGED")
    cols[3].metric("Review", "MERGED")
    cols[4].metric("Facebook", "MERGED")
    cols[5].metric("System", "v1.6")


def render_home() -> None:
    st.subheader("Command Center")
    st.write("Naz Lab is the main app. Workstations connect behind this single dashboard; phase apps stay as fallback backends while modules are merged.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Create")
        st.success("Text and Voice job workflows are inside Naz Lab.")
        st.write("Use Text to create content and Voice to create text-to-voice jobs or attach audio outputs.")
    with c2:
        st.markdown("### Visuals")
        st.success("Image Workstation controls are inside Naz Lab.")
        st.write("Use Image for runtime checks, queue generation, gallery, metadata, and job validation.")
    with c3:
        st.markdown("### Review & Publish")
        st.success("Review and Facebook Post controls are inside Naz Lab.")
        st.write("Create review packages, approve/export, then prepare Facebook handoff safely.")
    st.divider()
    render_review_panel()


def render_video() -> None:
    st.subheader("Video Generation")
    st.warning("Video generation is deferred. This section is planning-only until voice, text, image, and posting tools are fully ready.")
    c1, c2 = st.columns(2)
    c1.metric("Video jobs", count_files(VIDEO_JOBS))
    c2.metric("Video outputs", count_files(VIDEO_OUTPUTS))
    st.code("script -> scene plan -> image prompts -> generated images -> voice -> video manifest -> video backend later", language="text")
    st.button("Generate video", disabled=True)


def render_files() -> None:
    st.subheader("Files / Outputs")
    areas = [
        ("Image jobs", IMAGE_JOBS, JSON_EXTENSIONS),
        ("Image outputs", IMAGE_OUTPUTS, IMAGE_EXTENSIONS),
        ("Voice jobs", VOICE_JOBS, JSON_EXTENSIONS),
        ("Voice outputs", VOICE_OUTPUTS, AUDIO_EXTENSIONS),
        ("Video jobs", VIDEO_JOBS, JSON_EXTENSIONS),
        ("Video outputs", VIDEO_OUTPUTS, JSON_EXTENSIONS),
        ("Config", CONFIG_DIR, JSON_EXTENSIONS),
        ("Logs", LOGS_DIR, JSON_EXTENSIONS | {".log", ".txt"}),
        ("Review packages", BASE_PATH / "final_packages", JSON_EXTENSIONS),
    ]
    rows = [{"Area": label, "Path": str(path), "Files": count_files(path), "Status": "ready" if path.exists() else "missing"} for label, path, _ in areas]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected_area = st.selectbox("Browse area", [row["Area"] for row in rows])
    selected = next(item for item in areas if item[0] == selected_area)
    area_rows = file_rows(selected[1], selected[2])
    if area_rows:
        st.dataframe(area_rows, use_container_width=True, hide_index=True)
    else:
        st.info(f"No matching files found in {selected[1]}")


def render_health_logs() -> None:
    st.subheader("Health / Logs")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Workstation links")
        st.json(safe_json(WORKSTATION_LINKS_JSON, {}))
    with c2:
        st.markdown("### Package index")
        st.json(safe_json(BASE_PATH / "final_packages" / "package_index.json", {"items": []}))
    rows = file_rows(LOGS_DIR, JSON_EXTENSIONS | {".log", ".txt"})
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)


def render_runbook() -> None:
    st.subheader("Runbook")
    st.code(
        """Naz Lab is the main command center.
Text, Voice job workflow, Image, Review, and Facebook Post controls are merged into this dashboard.
No tab named Complete Package.
Voice real TTS engine is pending connection; Drive-backed voice jobs and audio attachment are ready.
Video generation stays deferred.
Real Facebook posting stays disabled/manual-gated.
""",
        language="text",
    )
    for rule in [
        "Use the all-in-one launcher as the official entrypoint.",
        "Use Text tab for generation, saving, and Image Job handoff.",
        "Use Voice tab for text-to-voice jobs and audio output attachment.",
        "Use Image tab for runtime checks, queue generation, gallery, metadata, and job validation.",
        "Use Home review workflow for package create, preview, approve, and export.",
        "Use Facebook Post tab for approved package handoff, safe config, manual gate, and social log.",
        "Do not add a tab named Complete Package.",
        "Keep real Facebook posting disabled/manual-gated.",
        "Keep video generation locked/deferred for now.",
    ]:
        st.checkbox(rule, value=True, disabled=True)


def main() -> None:
    st.set_page_config(page_title="Naz Lab", page_icon="🧪", layout="wide")
    render_css()
    render_header()
    render_status_strip()
    tabs = st.tabs(["Home", "Text", "Voice", "Image", "Video", "Facebook Post", "Files", "Health / Logs", "Runbook"])
    with tabs[0]:
        render_home()
    with tabs[1]:
        render_text_panel()
    with tabs[2]:
        render_voice_panel()
    with tabs[3]:
        render_image_panel()
    with tabs[4]:
        render_video()
    with tabs[5]:
        render_facebook_panel()
    with tabs[6]:
        render_files()
    with tabs[7]:
        render_health_logs()
    with tabs[8]:
        render_runbook()


if __name__ == "__main__":
    main()
