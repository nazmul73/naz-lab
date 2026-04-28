"""Naz Lab Master Dashboard Phase 2.21.

Adds Phase 3.1 Real Image Backend UI:
- runtime status
- queued job selection
- real image generation button
- output PNG gallery
- metadata/job JSON preview

Requires Colab GPU and diffusers dependencies for real generation.
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

from image_workstation.real_image_backend_phase31 import (  # noqa: E402
    DEFAULT_MODEL_ID,
    process_pending_real_image_jobs,
    process_real_image_job,
    runtime_status,
)
from shared.drive_paths import IMAGE_JOBS, IMAGE_OUTPUTS, LOGS_DIR, WORKSTATION_LINKS_JSON  # noqa: E402
from shared.job_queue_schema import read_json, summarize_job_file, validate_job_record  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402

PHASE = "2.21"
PHASE_STATUS = "real-image-backend-phase-3-1-ready"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def json_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def latest_jobs() -> list[Path]:
    if not IMAGE_JOBS.exists():
        return []
    return sorted(IMAGE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def latest_images() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    return sorted([p for p in IMAGE_OUTPUTS.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS], key=lambda p: p.stat().st_mtime, reverse=True)


def latest_metadata() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    return sorted(IMAGE_OUTPUTS.glob("*.metadata.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def render_runtime() -> None:
    st.header("Real Image Backend Runtime")
    status = runtime_status()
    c1, c2, c3 = st.columns(3)
    c1.metric("CUDA", "yes" if status.get("cuda_available") else "no")
    c2.metric("Torch", "yes" if status.get("torch_available") else "no")
    c3.metric("Diffusers", "yes" if status.get("diffusers_available") else "no")
    st.json(status)
    if not status.get("cuda_available"):
        st.warning("CUDA GPU is required for real image generation. Connect Colab GPU before running generation.")


def render_generate() -> None:
    st.header("Generate Real Images from Queue")
    rows = [summarize_job_file(path) for path in latest_jobs()]
    queued = [row for row in rows if row.get("Status") in ["created", "queued", "failed"] and row.get("Valid")]
    st.metric("Processable valid jobs", len(queued))
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    model_id = st.text_input("Diffusers model ID", value=DEFAULT_MODEL_ID)
    col_a, col_b = st.columns(2)
    with col_a:
        if queued:
            selected = Path(st.selectbox("Select one job", [row["Path"] for row in queued]))
            if st.button("Generate selected job", type="primary"):
                with st.spinner("Generating image. This can take 1-3 minutes on Colab GPU..."):
                    result = process_real_image_job(selected, model_id=model_id)
                st.json(result)
        else:
            st.info("No queued valid jobs found.")
    with col_b:
        limit = st.number_input("Batch limit", min_value=1, max_value=10, value=1, step=1)
        if st.button("Generate batch"):
            with st.spinner("Generating batch..."):
                result = process_pending_real_image_jobs(limit=int(limit), model_id=model_id)
            st.json(result)


def render_gallery() -> None:
    st.header("Generated Image Gallery")
    images = latest_images()
    metadata_files = latest_metadata()
    c1, c2 = st.columns(2)
    c1.metric("Images", len(images))
    c2.metric("Metadata files", len(metadata_files))
    if images:
        cols = st.columns(3)
        for i, path in enumerate(images[:60]):
            with cols[i % 3]:
                st.image(str(path), caption=path.name, use_container_width=True)
                st.download_button("Download PNG", data=path.read_bytes(), file_name=path.name, mime="image/png", key=f"download_{i}")
    else:
        st.info("No real generated images yet.")
    st.markdown("### Metadata")
    if metadata_files:
        selected = Path(st.selectbox("Open metadata", [str(p) for p in metadata_files]))
        data = read_json(selected, {})
        st.download_button("Download metadata JSON", data=json_text(data), file_name=selected.name, mime="application/json")
        st.json(data)


def render_job_preview() -> None:
    st.header("Job Preview / Validation")
    jobs = latest_jobs()
    if not jobs:
        st.info("No image jobs found.")
        return
    selected = Path(st.selectbox("Open job", [str(p) for p in jobs]))
    data = read_json(selected, {})
    ok, messages = validate_job_record(data)
    st.success("Schema valid") if ok else st.warning("Schema warnings: " + "; ".join(messages))
    st.json(data)
    output_path = Path(str(data.get("output_path", ""))) if isinstance(data, dict) and data.get("output_path") else None
    if output_path and output_path.exists() and output_path.suffix.lower() in IMAGE_EXTENSIONS:
        st.image(str(output_path), caption=output_path.name, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Naz Lab Real Image Backend", page_icon="🎨", layout="wide")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": now_iso()})
    st.title("🎨 Naz Lab Real Image Backend")
    st.caption("Dashboard Phase 2.21 / Real Image Backend Phase 3.1")
    tabs = st.tabs(["Runtime", "Generate", "Gallery", "Job Preview"])
    with tabs[0]:
        render_runtime()
    with tabs[1]:
        render_generate()
    with tabs[2]:
        render_gallery()
    with tabs[3]:
        render_job_preview()


if __name__ == "__main__":
    main()
