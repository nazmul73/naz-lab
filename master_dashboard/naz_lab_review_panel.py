"""Contextual Review Package panel for the Naz Lab dashboard.

No separate Complete Package tab is used. This panel is embedded inside the
Naz Lab workflow so package creation, preview, approval, and export happen from
within the main command center.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from final_package.package_backend import (
    APPROVED_PACKAGES_JSON,
    approve_package,
    build_auto_package,
    build_manual_prompt_package,
    build_reference_package,
    export_package,
    latest_image_jobs,
    latest_image_outputs,
    latest_text_outputs,
    list_packages,
    package_preview,
)
from master_dashboard.naz_lab_nav import render_nav
from shared.job_queue_schema import read_json

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def json_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def package_rows() -> list[dict[str, Any]]:
    return list_packages()


def render_package_summary() -> None:
    rows = package_rows()
    approved = read_json(APPROVED_PACKAGES_JSON, {"items": []}) if APPROVED_PACKAGES_JSON.exists() else {"items": []}
    approved_items = approved.get("items", []) if isinstance(approved, dict) and isinstance(approved.get("items"), list) else []
    ready_count = len([row for row in rows if row.get("Status") == "ready"])
    approved_count = len([row for row in rows if row.get("Status") == "approved"])
    exported_count = len([row for row in rows if row.get("Status") == "exported"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Packages", len(rows))
    c2.metric("Ready", ready_count)
    c3.metric("Approved", max(approved_count, len(approved_items)))
    c4.metric("Exported", exported_count)


def render_quick_package_builder() -> None:
    st.markdown("### Create review package")
    mode = st.radio("Package source", ["Auto from text + image job", "Manual prompt", "Reference image"], horizontal=True, key="review_package_mode")
    project = st.text_input("Project", value="General Bangla", key="review_project")
    topic = st.text_area("Topic", value="Review-ready Naz Lab content package", height=80, key="review_topic")

    if mode == "Auto from text + image job":
        text_files = latest_text_outputs()
        job_files = latest_image_jobs()
        text_path = st.selectbox("Text output path", [""] + [str(path) for path in text_files], key="review_text_path")
        job_path = st.selectbox("Image job path", [""] + [str(path) for path in job_files], key="review_job_path")
        if job_path:
            job = read_json(Path(job_path), {})
            st.markdown("#### Selected image job")
            st.json(job)
        if st.button("Create auto review package", type="primary", key="create_auto_review_package"):
            path = build_auto_package(project=project, topic=topic, text_output_path=text_path, image_job_path=job_path)
            st.success(f"Review package created: {path}")
            st.json(read_json(path, {}))

    elif mode == "Manual prompt":
        prompt = st.text_area("Manual image prompt", value="A clean premium social media visual for a Bangladeshi small business owner using AI tools.", height=140, key="review_manual_prompt")
        caption = st.text_area("Caption / post text", value="", height=110, key="review_manual_caption")
        images = latest_image_outputs()
        image_path = st.selectbox("Attach generated image optional", [""] + [str(path) for path in images], key="review_manual_image")
        if image_path:
            st.image(image_path, caption=Path(image_path).name, use_container_width=True)
        if st.button("Create manual review package", type="primary", key="create_manual_review_package"):
            path = build_manual_prompt_package(project=project, topic=topic, manual_prompt=prompt, generated_image_path=image_path, caption_text=caption)
            st.success(f"Review package created: {path}")
            st.json(read_json(path, {}))

    else:
        prompt = st.text_area("Manual image prompt", value="Use the reference image mood/composition and create a clean AI productivity social media visual.", height=140, key="review_ref_prompt")
        reference_raw = st.text_area("Reference image paths, one per line", value="", height=120, key="review_ref_paths")
        reference_paths = [line.strip() for line in reference_raw.splitlines() if line.strip()]
        for ref in reference_paths:
            path = Path(ref)
            if path.exists() and path.suffix.lower() in IMAGE_EXTENSIONS:
                st.image(str(path), caption=path.name, use_container_width=True)
            elif ref:
                st.warning(f"Reference path not found or not image: {ref}")
        images = latest_image_outputs()
        image_path = st.selectbox("Attach generated image optional", [""] + [str(path) for path in images], key="review_ref_image")
        if st.button("Create reference review package", type="primary", key="create_reference_review_package"):
            path = build_reference_package(project=project, topic=topic, manual_prompt=prompt, reference_paths=reference_paths, generated_image_path=image_path)
            st.success(f"Review package created: {path}")
            st.json(read_json(path, {}))


def render_preview_approve_export() -> None:
    st.markdown("### Review / approve / export")
    rows = package_rows()
    if not rows:
        st.info("No review packages yet. Create one above or generate content from Text/Image first.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    package_path = st.selectbox("Open review package", [row["Path"] for row in rows], key="review_open_package")
    preview = package_preview(package_path)
    record = preview.get("record", {}) if isinstance(preview, dict) else {}
    st.markdown("#### Package JSON")
    st.json(record)
    st.download_button("Download package JSON", data=json_text(record), file_name=Path(package_path).name, mime="application/json", key="review_download_json")
    if preview.get("text_preview"):
        st.markdown("#### Text preview")
        st.text_area("Text", preview.get("text_preview", ""), height=240, key="review_text_preview")
    image_path = Path(str(record.get("generated_image_path", ""))) if isinstance(record, dict) and record.get("generated_image_path") else None
    if image_path and image_path.exists() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
        st.markdown("#### Image preview")
        st.image(str(image_path), caption=image_path.name, use_container_width=True)
        st.download_button("Download image", data=image_path.read_bytes(), file_name=image_path.name, key="review_download_image")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Approve review package", key="review_approve_package"):
            result = approve_package(package_path, note="approved from Naz Lab dashboard")
            st.success("Review package approved")
            st.json(result)
    with col_b:
        if st.button("Export review package", key="review_export_package"):
            result = export_package(package_path)
            st.success("Review package exported")
            st.json(result)


def render_approved_list() -> None:
    st.markdown("### Approved package list")
    data = read_json(APPROVED_PACKAGES_JSON, {"items": []}) if APPROVED_PACKAGES_JSON.exists() else {"items": []}
    st.json(data)
    st.download_button("Download approved_packages.json", data=json_text(data), file_name="approved_packages.json", mime="application/json", key="review_approved_download")


def render_review_panel() -> None:
    st.markdown("## Review Package Workflow")
    st.caption("Contextual package/review actions inside Naz Lab. This is not a separate Complete Package tab.")
    render_package_summary()
    selected = render_nav(["Create", "Preview / Approve / Export", "Approved"], key="review_sub", variant="sub")
    if selected == "Create":
        render_quick_package_builder()
    elif selected == "Preview / Approve / Export":
        render_preview_approve_export()
    elif selected == "Approved":
        render_approved_list()
