"""Naz Lab Image Workstation Phase 3.1.

Polished queue app for reading image job queue items from Drive,
previewing prompts, applying visual presets, updating job status,
and viewing image outputs.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    IMAGE_PROMPTS,
    OUTPUT_LOG_JSON,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import append_output_log, safe_read_json, safe_write_json, update_workstation_status  # noqa: E402

PHASE = "3.1"
STATUS_OPTIONS = ["pending", "in_progress", "completed", "blocked", "archived"]
PRESET_OPTIONS = ["General Bangladeshi", "True Noir", "ToolFlow", "Rangpur/Nilphamari", "Custom"]

VISUAL_REQUIREMENTS = {
    "Primary culture": "Bangladeshi visual context by default.",
    "Regional flavor": "Rangpur/Nilphamari/North Bengal visual details when regional context is useful.",
    "True Noir style": "Adult-only, cinematic, moody, realistic, no gore, no dead body, no visible wounds.",
    "ToolFlow style": "Clean SaaS/productivity visuals, premium, minimal, practical, non-hype.",
    "Text safety": "Avoid logos, fake official marks, unreadable text clutter, and unnecessary captions inside images.",
}

PRESET_TEXT = {
    "General Bangladeshi": "Bangladeshi people, local environment, realistic cinematic composition, culturally grounded details, natural clothing and setting.",
    "True Noir": "true crime noir cinematic, adult subjects only, Bangladeshi setting, moody light, dramatic shadows, realistic emotional tension, no blood, no gore, no dead body, no visible wounds.",
    "ToolFlow": "clean SaaS productivity visual, premium minimal dashboard feel, modern workspace, practical technology theme, no hype, no clutter.",
    "Rangpur/Nilphamari": "North Bengal / Rangpur / Nilphamari regional atmosphere, grounded Bangladeshi people, rural or small-town texture when relevant, natural light, authentic local context.",
    "Custom": "Write custom visual direction in the notes field.",
}


def read_json(path: Path, default: Any) -> Any:
    try:
        return safe_read_json(path, default)
    except Exception:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default


def list_job_files() -> list[Path]:
    if not IMAGE_JOBS.exists():
        return []
    files = [path for path in IMAGE_JOBS.glob("*.json") if path.is_file()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)


def list_image_files() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend([path for path in IMAGE_OUTPUTS.glob(pattern) if path.is_file()])
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)


def job_counts(jobs: list[Path]) -> dict[str, int]:
    counts = {status: 0 for status in STATUS_OPTIONS}
    for path in jobs:
        data = read_json(path, {})
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        counts[status] = counts.get(status, 0) + 1
    return counts


def write_job(path: Path, data: dict[str, Any]) -> None:
    data["last_updated"] = datetime.now().isoformat(timespec="seconds")
    safe_write_json(path, data)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="image_workstation",
        event="job_updated",
        details={"job_file": str(path), "status": data.get("status", "unknown"), "preset": data.get("visual_preset", "")},
    )


def build_enhanced_prompt(base_prompt: str, preset: str, custom_note: str = "") -> str:
    preset_note = PRESET_TEXT.get(preset, "")
    parts = [base_prompt.strip()]
    if preset_note:
        parts.append(f"Visual preset: {preset_note}")
    if custom_note.strip():
        parts.append(f"Additional direction: {custom_note.strip()}")
    parts.append("Quality rules: realistic, clean composition, culturally grounded, no fake logos, no unnecessary text inside image.")
    return "\n\n".join(part for part in parts if part)


def render_header() -> None:
    st.set_page_config(page_title="Naz Lab Image Workstation", page_icon="🎨", layout="wide")
    st.title("🎨 Naz Lab Image Workstation")
    st.caption("Phase 3.1 — polished queue, prompt presets, status control, output library.")
    st.info("Bangladeshi visuals by default. Regional context defaults to Rangpur/Nilphamari/North Bengal when useful.")


def render_status() -> None:
    st.header("Status")
    jobs = list_job_files()
    images = list_image_files()
    counts = job_counts(jobs)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Phase", PHASE)
    c2.metric("Job files", len(jobs))
    c3.metric("Pending", counts.get("pending", 0))
    c4.metric("In progress", counts.get("in_progress", 0))
    c5.metric("Image outputs", len(images))

    c6, c7, c8 = st.columns(3)
    c6.metric("Completed", counts.get("completed", 0))
    c7.metric("Blocked", counts.get("blocked", 0))
    c8.metric("Archived", counts.get("archived", 0))

    st.markdown("### Visual requirements")
    st.json(VISUAL_REQUIREMENTS)

    st.markdown("### Presets")
    st.json(PRESET_TEXT)

    with st.expander("Paths", expanded=False):
        st.write({
            "base_path": str(BASE_PATH),
            "image_jobs": str(IMAGE_JOBS),
            "image_prompts": str(IMAGE_PROMPTS),
            "image_outputs": str(IMAGE_OUTPUTS),
            "workstation_links_json": str(WORKSTATION_LINKS_JSON),
        })


def render_queue() -> None:
    st.header("Image job queue")
    jobs = list_job_files()
    if not jobs:
        st.info("No image jobs found. Use Text Workstation > Prompt Improver to create image jobs.")
        return

    rows = []
    for path in jobs:
        data = read_json(path, {})
        rows.append({
            "File": path.name,
            "Status": data.get("status", "unknown") if isinstance(data, dict) else "unknown",
            "Preset": data.get("visual_preset", "") if isinstance(data, dict) else "",
            "Created": data.get("created_at", "") if isinstance(data, dict) else "",
            "Source": data.get("source_workstation", "") if isinstance(data, dict) else "",
            "Mode": data.get("source_mode", "") if isinstance(data, dict) else "",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    selected_name = st.selectbox("Select job", [path.name for path in jobs])
    selected_path = IMAGE_JOBS / selected_name
    data = read_json(selected_path, {})
    if not isinstance(data, dict):
        st.error("Selected job JSON could not be read.")
        return

    prompt = data.get("prompt", "")
    current_preset = data.get("visual_preset", "General Bangladeshi")
    preset_index = PRESET_OPTIONS.index(current_preset) if current_preset in PRESET_OPTIONS else 0

    st.markdown("### Job card")
    c1, c2, c3 = st.columns(3)
    c1.metric("Status", data.get("status", "unknown"))
    c2.metric("Source", data.get("source_workstation", "unknown"))
    c3.metric("Preset", current_preset)

    st.markdown("### Copy-ready base prompt")
    st.text_area("Base prompt", prompt, height=180, help="Copy this prompt into an image generator if needed.")

    with st.form("update_job_form"):
        status = st.selectbox("Job status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(data.get("status", "pending")) if data.get("status", "pending") in STATUS_OPTIONS else 0)
        preset = st.selectbox("Visual preset", PRESET_OPTIONS, index=preset_index)
        custom_direction = st.text_area("Custom / regional / brand direction", value=data.get("custom_direction", ""), height=100)
        enhanced_prompt = build_enhanced_prompt(prompt, preset, custom_direction)
        st.text_area("Enhanced prompt preview", enhanced_prompt, height=220)
        output_path = st.text_input("Output image path", value=data.get("output_path", ""))
        notes = st.text_area("Notes", value=data.get("notes", ""), height=100)
        submitted = st.form_submit_button("Save job update")

    if submitted:
        data["status"] = status
        data["visual_preset"] = preset
        data["custom_direction"] = custom_direction.strip()
        data["enhanced_prompt"] = enhanced_prompt
        data["output_path"] = output_path.strip()
        data["notes"] = notes.strip()
        write_job(selected_path, data)
        st.success("Job updated.")
        st.rerun()

    with st.expander("Raw job JSON", expanded=False):
        st.json(data)


def render_outputs() -> None:
    st.header("Image outputs")
    images = list_image_files()
    if not images:
        st.info("No generated images found yet.")
        st.caption(str(IMAGE_OUTPUTS))
        return

    selected = st.selectbox("Select image", [path.name for path in images])
    path = IMAGE_OUTPUTS / selected
    st.caption(str(path))
    try:
        image = Image.open(path)
        st.image(image, caption=path.name, use_container_width=True)
        st.write({"width": image.width, "height": image.height, "format": image.format})
    except Exception as exc:
        st.error(f"Could not open image: {exc}")


def render_prompt_library() -> None:
    st.header("Prompt library")
    prompt_files = []
    if IMAGE_PROMPTS.exists():
        prompt_files = sorted([path for path in IMAGE_PROMPTS.glob("*.txt") if path.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)
    if not prompt_files:
        st.info("No saved image prompt text files yet.")
        return
    selected = st.selectbox("Select prompt file", [path.name for path in prompt_files])
    path = IMAGE_PROMPTS / selected
    st.caption(str(path))
    st.text_area("Prompt file preview", path.read_text(encoding="utf-8", errors="ignore"), height=320)


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("This Phase 3.1 version manages the queue and output library. It does not generate images yet.")
    st.markdown("Next build: generator backend integration after queue workflow is stable.")
    st.code("streamlit run image_workstation/app.py --server.port 8503 --server.address 0.0.0.0", language="bash")


def main() -> None:
    render_header()
    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "image_workstation",
        {"status": "running", "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")},
    )
    tabs = st.tabs(["Status", "Queue", "Outputs", "Prompt Library", "Launch"])
    with tabs[0]:
        render_status()
    with tabs[1]:
        render_queue()
    with tabs[2]:
        render_outputs()
    with tabs[3]:
        render_prompt_library()
    with tabs[4]:
        render_launch()


if __name__ == "__main__":
    main()
