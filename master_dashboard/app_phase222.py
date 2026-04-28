"""Naz Lab Dashboard Phase 2.22 — Final Content Package Flow.

Covers final package flow items 1-10:
- package schema/backend UI
- auto package flow
- manual prompt package mode
- manual prompt + reference image mode
- package preview
- generated image + text + metadata linking
- export/download
- approved package list
- polished final package dashboard tab
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from final_package.package_backend import (  # noqa: E402
    APPROVED_PACKAGES_JSON,
    PACKAGE_DIR,
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
from shared.drive_paths import IMAGE_OUTPUTS, WORKSTATION_LINKS_JSON  # noqa: E402
from shared.job_queue_schema import read_json  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402

PHASE = "2.22"
PHASE_STATUS = "final-content-package-flow-ready"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def json_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def image_files() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    return sorted([p for p in IMAGE_OUTPUTS.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS], key=lambda p: p.stat().st_mtime, reverse=True)


def render_home() -> None:
    st.header("Final Content Package Flow")
    rows = list_packages()
    c1, c2, c3 = st.columns(3)
    c1.metric("Packages", len(rows))
    c2.metric("Generated images", len(image_files()))
    c3.metric("Package folder", "ready" if PACKAGE_DIR.exists() else "missing")
    st.success("Package builder backend and frontend are connected.")
    st.info("Use Auto Package for normal workflow. Use Manual Prompt or Reference Image mode when you want a separate image prompt or reference-based package.")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)


def render_auto_package() -> None:
    st.header("Auto Package Builder")
    text_files = latest_text_outputs()
    job_files = latest_image_jobs()
    if not job_files:
        st.warning("No image jobs found. Create an image job from Text Workstation first.")
    project = st.text_input("Project", value="General Bangla")
    topic = st.text_area("Topic", value="একজন ছোট ব্যবসায়ী AI tools ব্যবহার করে প্রতিদিনের content planning সহজ করে ফেলল।", height=90)
    text_path = st.selectbox("Text output path", [""] + [str(path) for path in text_files])
    job_path = st.selectbox("Image job path", [""] + [str(path) for path in job_files])
    if job_path:
        job = read_json(Path(job_path), {})
        st.markdown("### Selected image job")
        st.json(job)
        output_path = Path(str(job.get("output_path", ""))) if isinstance(job, dict) and job.get("output_path") else None
        if output_path and output_path.exists() and output_path.suffix.lower() in IMAGE_EXTENSIONS:
            st.image(str(output_path), caption=output_path.name, use_container_width=True)
    if st.button("Build Auto Package", type="primary"):
        path = build_auto_package(project=project, topic=topic, text_output_path=text_path, image_job_path=job_path)
        st.success(f"Package created: {path}")
        st.json(read_json(path, {}))


def render_manual_package() -> None:
    st.header("Manual Prompt Package")
    project = st.text_input("Project", value="General Bangla", key="manual_project")
    topic = st.text_area("Topic", value="Manual image prompt package", height=80, key="manual_topic")
    prompt = st.text_area("Manual image prompt", value="A Bangladeshi small business owner using AI tools on a laptop, clean modern productivity style, realistic, premium social media visual", height=150)
    caption = st.text_area("Caption / post text", value="", height=120)
    existing_images = image_files()
    generated_image_path = st.selectbox("Attach generated image path optional", [""] + [str(path) for path in existing_images])
    if generated_image_path:
        st.image(generated_image_path, caption=Path(generated_image_path).name, use_container_width=True)
    if st.button("Build Manual Prompt Package", type="primary"):
        path = build_manual_prompt_package(project=project, topic=topic, manual_prompt=prompt, generated_image_path=generated_image_path, caption_text=caption)
        st.success(f"Manual package created: {path}")
        st.json(read_json(path, {}))


def render_reference_package() -> None:
    st.header("Manual Prompt + Reference Image Package")
    st.caption("Provide reference image file paths from Drive/Colab. Uploaded file support can be added later; this version uses path-based references for persistent storage.")
    project = st.text_input("Project", value="General Bangla", key="ref_project")
    topic = st.text_area("Topic", value="Reference image based package", height=80, key="ref_topic")
    prompt = st.text_area("Manual image prompt", value="Use the reference image mood/composition and create a clean social media visual", height=150, key="ref_prompt")
    reference_raw = st.text_area("Reference image paths, one per line", value="", height=120)
    reference_paths = [line.strip() for line in reference_raw.splitlines() if line.strip()]
    for ref in reference_paths:
        path = Path(ref)
        if path.exists() and path.suffix.lower() in IMAGE_EXTENSIONS:
            st.image(str(path), caption=path.name, use_container_width=True)
        elif ref:
            st.warning(f"Reference path not found or not image: {ref}")
    existing_images = image_files()
    generated_image_path = st.selectbox("Attach generated image path optional", [""] + [str(path) for path in existing_images], key="ref_generated")
    if st.button("Build Reference Package", type="primary"):
        path = build_reference_package(project=project, topic=topic, manual_prompt=prompt, reference_paths=reference_paths, generated_image_path=generated_image_path)
        st.success(f"Reference package created: {path}")
        st.json(read_json(path, {}))


def render_package_preview() -> None:
    st.header("Package Preview / Export / Approve")
    rows = list_packages()
    if not rows:
        st.info("No packages yet.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    package_path = st.selectbox("Open package", [row["Path"] for row in rows])
    preview = package_preview(package_path)
    record = preview.get("record", {}) if isinstance(preview, dict) else {}
    st.markdown("### Package JSON")
    st.json(record)
    st.download_button("Download package JSON", data=json_text(record), file_name=Path(package_path).name, mime="application/json")
    if preview.get("text_preview"):
        st.markdown("### Text preview")
        st.text_area("Text", preview.get("text_preview", ""), height=260)
    image_path = Path(str(record.get("generated_image_path", ""))) if isinstance(record, dict) and record.get("generated_image_path") else None
    if image_path and image_path.exists() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
        st.markdown("### Image preview")
        st.image(str(image_path), caption=image_path.name, use_container_width=True)
        st.download_button("Download image", data=image_path.read_bytes(), file_name=image_path.name, mime="image/png")
    ref_images = record.get("reference_images", []) if isinstance(record, dict) else []
    if isinstance(ref_images, list) and ref_images:
        st.markdown("### Reference images")
        for ref in ref_images:
            path = Path(str(ref))
            if path.exists() and path.suffix.lower() in IMAGE_EXTENSIONS:
                st.image(str(path), caption=path.name, use_container_width=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Approve package"):
            st.success("Package approved")
            st.json(approve_package(package_path, note="approved from Dashboard Phase 2.22"))
    with col_b:
        if st.button("Export package"):
            st.success("Package exported")
            st.json(export_package(package_path))


def render_approved_packages() -> None:
    st.header("Approved Package List")
    data = read_json(APPROVED_PACKAGES_JSON, {"items": []})
    st.json(data)
    st.download_button("Download approved_packages.json", data=json_text(data), file_name="approved_packages.json", mime="application/json")


def render_checklist() -> None:
    st.header("Final Content Package Flow Checklist")
    items = [
        "Final package schema ready",
        "Package Builder backend ready",
        "Auto package flow connected",
        "Manual prompt image generation option represented",
        "Reference image input/support added",
        "Package Preview UI ready",
        "Generated image + text + metadata linking ready",
        "Package export/download ready",
        "Approved package list flow ready",
        "Dashboard final package tab polished",
    ]
    for item in items:
        st.checkbox(item, value=True, disabled=True)


def main() -> None:
    st.set_page_config(page_title="Naz Lab Final Packages", page_icon="📦", layout="wide")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE})
    st.title("📦 Naz Lab Final Content Package Flow")
    st.caption("Dashboard Phase 2.22 — auto/manual/reference packages, preview, approve, export")
    tabs = st.tabs(["Home", "Auto Package", "Manual Prompt", "Reference Image", "Preview / Export", "Approved", "Checklist"])
    with tabs[0]:
        render_home()
    with tabs[1]:
        render_auto_package()
    with tabs[2]:
        render_manual_package()
    with tabs[3]:
        render_reference_package()
    with tabs[4]:
        render_package_preview()
    with tabs[5]:
        render_approved_packages()
    with tabs[6]:
        render_checklist()


if __name__ == "__main__":
    main()
