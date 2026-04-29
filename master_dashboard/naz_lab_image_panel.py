"""Reusable Image Workstation panel for the Naz Lab dashboard.

This panel brings the Phase 3.1 image backend controls into the main Naz Lab
app so image testing can happen from the command center.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from image_workstation.real_image_backend_phase31 import (
    DEFAULT_MODEL_ID,
    process_pending_real_image_jobs,
    process_real_image_job,
    runtime_status,
)
from master_dashboard.naz_lab_nav import render_nav
from shared.drive_paths import BASE_PATH, IMAGE_JOBS, IMAGE_OUTPUTS
from shared.job_queue_schema import read_json, summarize_job_file, validate_job_record

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
JSON_EXTENSIONS = {".json"}
REFERENCE_IMAGE_DIR = BASE_PATH / "reference_images"


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def json_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def safe_upload_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ["_", "-", "."] else "_" for ch in name)


def save_uploaded_reference_image(uploaded_file) -> Path:
    REFERENCE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = REFERENCE_IMAGE_DIR / f"ref_image_{now_stamp()}_{safe_upload_name(uploaded_file.name)}"
    path.write_bytes(uploaded_file.getbuffer())
    return path


def latest_reference_images() -> list[Path]:
    if not REFERENCE_IMAGE_DIR.exists():
        return []
    files = [p for p in REFERENCE_IMAGE_DIR.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def latest_jobs() -> list[Path]:
    if not IMAGE_JOBS.exists():
        return []
    return sorted(IMAGE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def latest_images() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    files = [p for p in IMAGE_OUTPUTS.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def latest_metadata() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    files = [p for p in IMAGE_OUTPUTS.rglob("*") if p.is_file() and p.suffix.lower() == ".json"]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def render_runtime() -> None:
    st.markdown("### Runtime")
    status = runtime_status()
    c1, c2, c3 = st.columns(3)
    c1.metric("CUDA", "yes" if status.get("cuda_available") else "no")
    c2.metric("Torch", "yes" if status.get("torch_available") else "no")
    c3.metric("Diffusers", "yes" if status.get("diffusers_available") else "no")
    st.json(status)
    if not status.get("cuda_available"):
        st.warning("CUDA GPU is required for real image generation. Queue, gallery, and metadata views still work on CPU.")


def render_generate() -> None:
    st.markdown("### Generate from Image Job Queue")
    jobs = latest_jobs()
    rows = [summarize_job_file(path) for path in jobs]
    processable = [row for row in rows if row.get("Status") in ["created", "queued", "failed"] and row.get("Valid")]
    st.metric("Processable valid jobs", len(processable))
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info(f"No image job JSON files found in {IMAGE_JOBS}")
    model_id = st.text_input("Diffusers model ID", value=DEFAULT_MODEL_ID, key="naz_image_model_id")
    col_a, col_b = st.columns(2)
    with col_a:
        if processable:
            selected = Path(st.selectbox("Select one job", [row["Path"] for row in processable], key="naz_image_selected_job"))
            if st.button("Generate selected job", type="primary", key="naz_image_generate_selected"):
                with st.spinner("Generating image. Use Colab GPU for this step..."):
                    result = process_real_image_job(selected, model_id=model_id)
                st.json(result)
        else:
            st.info("No processable valid jobs found.")
    with col_b:
        limit = st.number_input("Batch limit", min_value=1, max_value=10, value=1, step=1, key="naz_image_batch_limit")
        if st.button("Generate batch", key="naz_image_generate_batch"):
            with st.spinner("Generating batch. Use Colab GPU for this step..."):
                result = process_pending_real_image_jobs(limit=int(limit), model_id=model_id)
            st.json(result)


def render_gallery() -> None:
    st.markdown("### Gallery")
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
                st.download_button("Download image", data=path.read_bytes(), file_name=path.name, key=f"naz_img_download_{i}")
    else:
        st.info(f"No generated images found in {IMAGE_OUTPUTS}")


def render_metadata() -> None:
    st.markdown("### Metadata")
    metadata_files = latest_metadata()
    if metadata_files:
        selected = Path(st.selectbox("Open metadata", [str(p) for p in metadata_files], key="naz_image_metadata_select"))
        data = read_json(selected, {})
        st.download_button("Download metadata JSON", data=json_text(data), file_name=selected.name, mime="application/json")
        st.json(data)
    else:
        st.info("No metadata JSON files found.")


def render_job_preview() -> None:
    st.markdown("### Job Preview / Validation")
    jobs = latest_jobs()
    if not jobs:
        st.info("No image jobs found.")
        return
    selected = Path(st.selectbox("Open job", [str(p) for p in jobs], key="naz_image_job_preview"))
    data = read_json(selected, {})
    ok, messages = validate_job_record(data)
    if ok:
        st.success("Schema valid")
    else:
        st.warning("Schema warnings: " + "; ".join(messages))
    st.json(data)
    output_path = Path(str(data.get("output_path", ""))) if isinstance(data, dict) and data.get("output_path") else None
    if output_path and output_path.exists() and output_path.suffix.lower() in IMAGE_EXTENSIONS:
        st.image(str(output_path), caption=output_path.name, use_container_width=True)


def render_reference_note() -> None:
    st.markdown("### Reference image support")
    st.caption("Reference image upload করলে ফাইল Drive-এর NazLab/reference_images folder-এ সেভ হবে এবং package/reference workflow-এ ব্যবহার করা যাবে।")
    uploaded = st.file_uploader("Upload reference image", type=["png", "jpg", "jpeg", "webp"], key="image_reference_upload")
    if uploaded is not None:
        if st.button("Save uploaded reference image", type="primary", key="save_reference_image"):
            saved = save_uploaded_reference_image(uploaded)
            st.success(f"Reference image saved: {saved}")
            st.image(str(saved), caption=saved.name, use_container_width=True)

    refs = latest_reference_images()
    st.metric("Reference images", len(refs))
    if refs:
        st.markdown("#### Reference image library")
        rows = [{"Name": p.name, "Path": str(p), "Size KB": round(p.stat().st_size / 1024, 1)} for p in refs]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        selected = Path(st.selectbox("Preview reference image", [str(p) for p in refs], key="image_reference_preview"))
        st.image(str(selected), caption=selected.name, use_container_width=True)
        st.code(str(selected), language="text")
    else:
        st.info(f"No reference images found in {REFERENCE_IMAGE_DIR}")


def render_image_panel() -> None:
    st.subheader("Image Generation")
    st.write("Create, inspect, generate, and review image jobs from inside Naz Lab. Heavy image generation requires Colab GPU and remains manually controlled.")
    selected = render_nav(["Runtime", "Generate", "Gallery", "Metadata", "Job Preview", "Reference"], key="image_sub", variant="sub")
    if selected == "Runtime":
        render_runtime()
    elif selected == "Generate":
        render_generate()
    elif selected == "Gallery":
        render_gallery()
    elif selected == "Metadata":
        render_metadata()
    elif selected == "Job Preview":
        render_job_preview()
    elif selected == "Reference":
        render_reference_note()
