"""Naz Lab unified command center shell.

This is the official app-style dashboard for the Naz Lab workspace. It is not
just a launcher map: it is the main control surface that will connect the
workstations behind one interface.

Current shell modules:
- Home
- Text
- Voice
- Image
- Video
- Facebook Post
- Files
- Health / Logs
- Runbook

Video generation is intentionally deferred. Real Facebook posting remains
manual-gated and disabled by default.
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
    CONFIG_DIR,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    IMAGE_PROMPTS,
    LOGS_DIR,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    VIDEO_JOBS,
    VIDEO_OUTPUTS,
    VOICE_JOBS,
    VOICE_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.job_queue_schema import read_json  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402

PHASE = "naz-lab-main-shell-1.1"
STATUS = "naz-lab-command-center-shell-ready"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
JSON_EXTENSIONS = {".json"}
TEXT_EXTENSIONS = {".txt", ".md", ".json"}

MODULES = [
    {
        "name": "Text",
        "status": "PASS",
        "summary": "Bangla-first text, script, prompt, and content output flow.",
        "backend": "text_workstation/app_official.py",
        "next": "Merge direct generation controls into this dashboard.",
    },
    {
        "name": "Voice",
        "status": "READY / VERIFY",
        "summary": "Text-to-voice workspace with Drive-backed jobs and outputs.",
        "backend": "voice workstation integration path pending marker",
        "next": "Connect existing voice backend and mark runtime PASS after verification.",
    },
    {
        "name": "Image",
        "status": "GPU PASS",
        "summary": "Image job queue, real image outputs, and metadata previews.",
        "backend": "master_dashboard/app_phase221.py",
        "next": "Bring controlled generation actions into this dashboard.",
    },
    {
        "name": "Video",
        "status": "DEFERRED",
        "summary": "Planning-only area. Real video generation is paused until the other tools are fully ready.",
        "backend": "future video workstation",
        "next": "Later: scene manifest, reel timeline, and generation backend.",
    },
    {
        "name": "Facebook Post",
        "status": "DRY-RUN PASS / GATED",
        "summary": "Manual-gated social handoff and blocked-post logging.",
        "backend": "master_dashboard/app_phase219.py",
        "next": "Keep real posting disabled unless explicitly configured and approved.",
    },
]

DRIVE_AREAS = [
    ("Text outputs", TEXT_OUTPUTS, TEXT_EXTENSIONS),
    ("Chat outputs", CHAT_OUTPUTS, TEXT_EXTENSIONS),
    ("Script outputs", SCRIPT_OUTPUTS, TEXT_EXTENSIONS),
    ("Image prompts", IMAGE_PROMPTS, TEXT_EXTENSIONS),
    ("Image jobs", IMAGE_JOBS, JSON_EXTENSIONS),
    ("Image outputs", IMAGE_OUTPUTS, IMAGE_EXTENSIONS),
    ("Voice jobs", VOICE_JOBS, JSON_EXTENSIONS),
    ("Voice outputs", VOICE_OUTPUTS, AUDIO_EXTENSIONS),
    ("Video jobs", VIDEO_JOBS, JSON_EXTENSIONS),
    ("Video outputs", VIDEO_OUTPUTS, {".json", ".txt", ".md"}),
    ("Config", CONFIG_DIR, JSON_EXTENSIONS),
    ("Logs", LOGS_DIR, JSON_EXTENSIONS | {".log", ".txt"}),
    ("Final packages", BASE_PATH / "final_packages", JSON_EXTENSIONS),
    ("Reference images", BASE_PATH / "reference_images", IMAGE_EXTENSIONS),
]

QUICK_ACTIONS = [
    {
        "label": "Open official Naz Lab app",
        "command": "%run /content/naz-lab/launchers/naz_lab_all_in_one_colab.py",
        "note": "Primary launcher for the single-dashboard flow.",
    },
    {
        "label": "Open image backend fallback",
        "command": "%run /content/naz-lab/launchers/phase3_1_real_image_backend_colab.py",
        "note": "Use only when real GPU image generation is needed.",
    },
]


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
        return {"error": str(exc), "path": str(path), "default": default}


def safe_text(path: Path, limit: int = 7000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:limit]
    except Exception as exc:
        return f"Could not read {path}: {exc}"


def file_rows(path: Path, extensions: set[str] | None = None, limit: int = 12) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in latest_files(path, extensions=extensions, limit=limit):
        rows.append(
            {
                "Name": item.name,
                "Path": str(item),
                "Modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(timespec="seconds"),
                "Size KB": round(item.stat().st_size / 1024, 1),
            }
        )
    return rows


def render_css() -> None:
    st.markdown(
        """
        <style>
          .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
          .naz-hero {
            padding: 1.4rem 1.5rem;
            border-radius: 26px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
          }
          .naz-hero h1 {margin:0; font-size:2.35rem; letter-spacing: -0.04em;}
          .naz-hero p {margin:0.45rem 0 0 0; opacity:0.92; font-size:1.04rem;}
          .naz-card {
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 20px;
            padding: 1rem 1rem;
            background: rgba(248, 250, 252, 0.78);
            margin-bottom: 0.75rem;
          }
          .naz-pill {
            display:inline-block;
            border-radius: 999px;
            padding: 0.22rem 0.65rem;
            font-size: 0.78rem;
            border: 1px solid rgba(148, 163, 184, 0.5);
            background: white;
            margin-right: 0.35rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "naz_lab",
        {"status": STATUS, "phase": PHASE, "last_seen": now_iso()},
    )
    st.markdown(
        """
        <div class="naz-hero">
          <h1>Naz Lab</h1>
          <p>Unified AI workstation command center for voice, text, image, video planning, Facebook handoff, files, and system health.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_strip() -> None:
    cols = st.columns(6)
    cols[0].metric("Text", "PASS")
    cols[1].metric("Voice", "READY")
    cols[2].metric("Image", "GPU PASS")
    cols[3].metric("Video", "DEFERRED")
    cols[4].metric("Facebook", "GATED")
    cols[5].metric("System", "v1.1 shell")


def render_home() -> None:
    st.subheader("Command Center")
    st.write("Use this dashboard as the main Naz Lab app. Individual phase apps remain available as fallback backends, but the product direction is one working command center.")
    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.markdown("### Workstation modules")
        for module in MODULES:
            with st.container(border=True):
                top_a, top_b = st.columns([2.2, 1])
                top_a.markdown(f"#### {module['name']}")
                top_b.metric("Status", module["status"])
                st.write(module["summary"])
                st.caption(f"Backend: {module['backend']}")
                st.caption(f"Next: {module['next']}")
    with c2:
        st.markdown("### Today’s operating rules")
        st.success("Text, image, package flow, and social dry-run are verified in the v1 flow.")
        st.info("Voice is represented in the main shell and should be connected to the completed voice backend before PASS marking.")
        st.warning("Video generation is paused. Keep the Video area planning-only until the other tools are fully ready.")
        st.warning("Real Facebook posting remains disabled/manual-gated.")
        st.markdown("### Quick commands")
        for action in QUICK_ACTIONS:
            st.caption(action["label"])
            st.code(action["command"], language="python")
            st.caption(action["note"])


def render_text() -> None:
    st.subheader("Text Workstation")
    st.write("Text outputs, script outputs, prompt assets, and image-job handoff files are visible here. Direct generation controls will be merged after the shell is verified.")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Text outputs", count_files(TEXT_OUTPUTS))
    col_b.metric("Script outputs", count_files(SCRIPT_OUTPUTS))
    col_c.metric("Image prompts", count_files(IMAGE_PROMPTS))
    tabs = st.tabs(["Text outputs", "Scripts", "Image prompts", "Image jobs"])
    folders = [TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS, IMAGE_JOBS]
    extensions = [TEXT_EXTENSIONS, TEXT_EXTENSIONS, TEXT_EXTENSIONS, JSON_EXTENSIONS]
    for tab, folder, ext in zip(tabs, folders, extensions):
        with tab:
            rows = file_rows(folder, ext)
            if rows:
                st.dataframe(rows, use_container_width=True, hide_index=True)
                selected = st.selectbox("Preview file", [row["Path"] for row in rows], key=f"text_{folder.name}")
                selected_path = Path(selected)
                if selected_path.suffix.lower() == ".json":
                    st.json(safe_json(selected_path, {}))
                else:
                    st.text_area("Preview", safe_text(selected_path), height=320)
            else:
                st.info(f"No files found in {folder}")


def render_voice() -> None:
    st.subheader("Voice / Text-to-Voice")
    st.write("Voice is part of the final Naz Lab command center. The shell is ready for Drive-backed voice jobs and audio outputs; connect the completed voice backend here before marking runtime PASS.")
    col_a, col_b = st.columns(2)
    col_a.metric("Voice jobs", count_files(VOICE_JOBS))
    col_b.metric("Voice outputs", count_files(VOICE_OUTPUTS))
    with st.container(border=True):
        st.markdown("### Text-to-voice control surface")
        voice_text = st.text_area("Text for voice generation", value="", height=140, placeholder="Paste narration text here...")
        preset = st.selectbox("Voice preset", ["Default", "Bangla narration", "English narration", "Custom"], index=0)
        st.button("Save voice job draft", disabled=True, help="Backend connection step pending in the unified dashboard shell.")
        st.caption(f"Draft length: {len(voice_text)} characters | Preset: {preset}")
    rows = file_rows(VOICE_OUTPUTS, AUDIO_EXTENSIONS)
    st.markdown("### Latest voice outputs")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        selected = st.selectbox("Open audio output", [row["Path"] for row in rows], key="voice_audio")
        st.audio(selected)
    else:
        st.info(f"No audio outputs found in {VOICE_OUTPUTS}")


def render_image() -> None:
    st.subheader("Image Generation")
    st.write("Use this area to inspect image jobs, generated images, and metadata. Real GPU generation remains controlled through the backend/fallback flow until direct controls are merged.")
    col_a, col_b = st.columns(2)
    col_a.metric("Image jobs", count_files(IMAGE_JOBS))
    col_b.metric("Generated images", len(latest_files(IMAGE_OUTPUTS, IMAGE_EXTENSIONS, limit=500)))
    tabs = st.tabs(["Jobs", "Gallery", "Metadata"])
    with tabs[0]:
        rows = file_rows(IMAGE_JOBS, JSON_EXTENSIONS, limit=20)
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
            selected = st.selectbox("Open image job", [row["Path"] for row in rows], key="image_job")
            st.json(safe_json(Path(selected), {}))
        else:
            st.info(f"No image jobs found in {IMAGE_JOBS}")
    with tabs[1]:
        images = latest_files(IMAGE_OUTPUTS, IMAGE_EXTENSIONS, limit=12)
        if images:
            cols = st.columns(3)
            for index, image_path in enumerate(images):
                with cols[index % 3]:
                    st.image(str(image_path), caption=image_path.name, use_container_width=True)
        else:
            st.info(f"No generated images found in {IMAGE_OUTPUTS}")
    with tabs[2]:
        rows = file_rows(IMAGE_OUTPUTS, JSON_EXTENSIONS, limit=20)
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
            selected = st.selectbox("Open image metadata", [row["Path"] for row in rows], key="image_metadata")
            st.json(safe_json(Path(selected), {}))
        else:
            st.info("No image metadata JSON files found.")


def render_video() -> None:
    st.subheader("Video Generation")
    st.warning("Video generation is deferred. This section is planning-only until voice, text, image, and posting tools are fully ready.")
    col_a, col_b = st.columns(2)
    col_a.metric("Video jobs", count_files(VIDEO_JOBS))
    col_b.metric("Video outputs", count_files(VIDEO_OUTPUTS))
    st.markdown("### Future video workflow")
    st.code(
        """script
-> scene plan
-> image prompts
-> generated images
-> voice/narration
-> video manifest
-> video generation backend later
""",
        language="text",
    )
    st.button("Generate video", disabled=True, help="Video generation is intentionally locked/deferred for now.")


def render_facebook_post() -> None:
    st.subheader("Facebook Post / Social Gate")
    st.write("Manual-gated posting controls live here. Real Facebook posting remains disabled by default; dry-run and blocked-post logs are the safe v1 behavior.")
    config_path = CONFIG_DIR / "facebook_graph_config.json"
    log_path = LOGS_DIR / "social_post_log.json"
    col_a, col_b = st.columns(2)
    config = safe_json(config_path, {}) if config_path.exists() else {}
    log = safe_json(log_path, {"items": []}) if log_path.exists() else {"items": []}
    col_a.metric("Config", "found" if config_path.exists() else "missing")
    col_b.metric("Log entries", len(log.get("items", [])) if isinstance(log, dict) and isinstance(log.get("items"), list) else 0)
    st.markdown("### Safe config")
    if config:
        st.json(config)
    else:
        st.info(f"No config file found yet at {config_path}. The backend creates the safe default when Social Gate runs.")
    st.markdown("### Social post log")
    st.json(log)
    st.caption("Fallback backend: master_dashboard/app_phase219.py")


def render_files() -> None:
    st.subheader("Files / Outputs")
    rows = []
    for label, path, extensions in DRIVE_AREAS:
        rows.append(
            {
                "Area": label,
                "Path": str(path),
                "Files": count_files(path),
                "Status": "ready" if path.exists() else "missing",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected_area = st.selectbox("Browse area", [row["Area"] for row in rows])
    selected = next(item for item in DRIVE_AREAS if item[0] == selected_area)
    area_rows = file_rows(selected[1], selected[2], limit=30)
    if area_rows:
        st.dataframe(area_rows, use_container_width=True, hide_index=True)
    else:
        st.info(f"No matching files found in {selected[1]}")


def render_health_logs() -> None:
    st.subheader("Health / Logs")
    st.write("System JSON, workstation links, package index, and logs are collected here for quick inspection.")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Workstation links")
        st.json(safe_json(WORKSTATION_LINKS_JSON, {}))
    with col_b:
        st.markdown("### Package index")
        st.json(safe_json(BASE_PATH / "final_packages" / "package_index.json", {"items": []}))
    st.markdown("### Latest logs")
    rows = file_rows(LOGS_DIR, JSON_EXTENSIONS | {".log", ".txt"}, limit=20)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        selected = st.selectbox("Open log", [row["Path"] for row in rows], key="health_log")
        selected_path = Path(selected)
        if selected_path.suffix.lower() == ".json":
            st.json(safe_json(selected_path, {}))
        else:
            st.text_area("Log preview", safe_text(selected_path), height=360)
    else:
        st.info(f"No logs found in {LOGS_DIR}")


def render_runbook() -> None:
    st.subheader("Runbook")
    st.markdown("### Naz Lab operating model")
    st.code(
        """Naz Lab is the main command center.
All workstations should connect behind this single app.
Text, voice, image, Facebook handoff, files, and health should be usable from this dashboard.
Video generation stays deferred until the other tools are fully ready.
""",
        language="text",
    )
    st.markdown("### Current rules")
    rules = [
        "Use the all-in-one launcher as the official entrypoint.",
        "Keep phase apps as fallback backends until the unified dashboard is fully verified.",
        "Keep real Facebook posting disabled/manual-gated.",
        "Keep video generation locked/deferred for now.",
        "Do not mark Voice runtime PASS until the voice backend is repo-integrated and Colab verified.",
    ]
    for rule in rules:
        st.checkbox(rule, value=True, disabled=True)


def main() -> None:
    st.set_page_config(page_title="Naz Lab", page_icon="🧪", layout="wide")
    render_css()
    render_header()
    render_status_strip()
    tabs = st.tabs([
        "Home",
        "Text",
        "Voice",
        "Image",
        "Video",
        "Facebook Post",
        "Files",
        "Health / Logs",
        "Runbook",
    ])
    with tabs[0]:
        render_home()
    with tabs[1]:
        render_text()
    with tabs[2]:
        render_voice()
    with tabs[3]:
        render_image()
    with tabs[4]:
        render_video()
    with tabs[5]:
        render_facebook_post()
    with tabs[6]:
        render_files()
    with tabs[7]:
        render_health_logs()
    with tabs[8]:
        render_runbook()


if __name__ == "__main__":
    main()
