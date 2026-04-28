"""Naz Lab Master Dashboard Phase 2.20.

Unified frontend dashboard for Frontend items 1-20.

Scope:
- simplified navigation
- queue/image/text/social/model/backend views in one app
- invalid old job filter/cleanup view
- generated image/manifest gallery
- social review image/output preview
- final package preview
- status cards
- real image backend control panel placeholder
- download buttons
- mobile-friendly layout and final checklist
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

from image_workstation.bridge_phase1 import process_pending_jobs  # noqa: E402
from shared.backend_health import build_health_summary  # noqa: E402
from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    CHAT_OUTPUTS,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    IMAGE_PROMPTS,
    LOGS_DIR,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.job_queue_schema import read_json, summarize_job_file, validate_job_record, write_json  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402
from shared.model_health import MODEL_HEALTH_JSON, RECOMMENDED_MODELS, build_model_health, pull_missing_models  # noqa: E402
from social_review.review_backend import (  # noqa: E402
    APPROVED_JOBS_JSON,
    REJECTED_JOBS_JSON,
    REVIEW_QUEUE_JSON,
    rebuild_review_queue,
    set_review_status,
)
from social_agent.facebook_graph_backend import (  # noqa: E402
    FACEBOOK_CONFIG_JSON,
    SOCIAL_POST_LOG_JSON,
    approved_items,
    ensure_config,
    gated_post_to_facebook,
)

PHASE = "2.20"
PHASE_STATUS = "unified-frontend-ready"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
TEXT_FOLDERS = [TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS, CHAT_OUTPUTS]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def json_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def file_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def latest_files(folder: Path, pattern: str = "*", limit: int = 300) -> list[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.rglob(pattern) if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def all_text_files() -> list[Path]:
    files: list[Path] = []
    for folder in TEXT_FOLDERS:
        files.extend(latest_files(folder, "*.txt", 300))
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def all_image_job_rows() -> list[dict[str, Any]]:
    files = latest_files(IMAGE_JOBS, "*.json", 2000)
    return [summarize_job_file(path) for path in files]


def all_output_manifest_files() -> list[Path]:
    return latest_files(IMAGE_OUTPUTS, "*.json", 500)


def all_real_image_files() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    images = [path for path in IMAGE_OUTPUTS.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS]
    return sorted(images, key=lambda p: p.stat().st_mtime, reverse=True)[:300]


def status_badge(value: bool) -> str:
    return "READY" if value else "NEEDS ACTION"


def render_top_status() -> None:
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": now_iso()})
    text_count = len(all_text_files())
    job_rows = all_image_job_rows()
    valid_jobs = sum(1 for row in job_rows if row.get("Valid"))
    invalid_jobs = len(job_rows) - valid_jobs
    done_jobs = sum(1 for row in job_rows if row.get("Status") == "done")
    approved_jobs = sum(1 for row in job_rows if row.get("Review") == "approved")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Text outputs", text_count)
    c2.metric("Image jobs", len(job_rows), f"{valid_jobs} valid")
    c3.metric("Done jobs", done_jobs)
    c4.metric("Approved", approved_jobs)

    if invalid_jobs:
        st.warning(f"Legacy/invalid jobs detected: {invalid_jobs}. Use Jobs > Invalid Jobs filter to inspect. Latest Phase 1.10 jobs remain valid.")
    else:
        st.success("All detected job JSON files validate against the current queue schema.")


def render_home() -> None:
    st.header("Status Summary")
    render_top_status()
    summary = build_health_summary()
    st.markdown("### System cards")
    c1, c2, c3 = st.columns(3)
    c1.info(f"Base Path\n\n{BASE_PATH}")
    c2.success("Text Workstation\n\nPhase 1.10 PASS")
    c3.success("Dashboard\n\nUnified Phase 2.20")
    st.markdown("### Backend health snapshot")
    st.json(summary)


def render_text_outputs() -> None:
    st.header("Text Output Browser")
    files = all_text_files()
    folder_filter = st.selectbox("Folder", ["All", "text_outputs", "script_outputs", "image_prompts", "chat_outputs"], index=0)
    keyword = st.text_input("Search text outputs", value="")
    if folder_filter != "All":
        files = [path for path in files if path.parent.name == folder_filter]
    if keyword:
        q = keyword.lower()
        files = [path for path in files if q in path.name.lower() or q in read_text(path).lower()]
    rows = [{"File": p.name, "Folder": p.parent.name, "Modified": file_mtime(p), "Path": str(p)} for p in files]
    st.metric("Matching text files", len(rows))
    if not rows:
        st.info("No matching text outputs found.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open text output", [row["Path"] for row in rows]))
    content = read_text(selected)
    st.download_button("Download TXT", data=content, file_name=selected.name, mime="text/plain")
    st.text_area("Preview", content, height=520)


def render_jobs() -> None:
    st.header("Image Jobs")
    rows = all_image_job_rows()
    view = st.radio("View", ["All", "Valid", "Invalid", "Queued", "Done", "Failed", "Approved", "Rejected"], horizontal=True)
    keyword = st.text_input("Search jobs", value="")
    if view == "Valid":
        rows = [row for row in rows if row.get("Valid")]
    elif view == "Invalid":
        rows = [row for row in rows if not row.get("Valid")]
    elif view in ["Queued", "Done", "Failed"]:
        rows = [row for row in rows if str(row.get("Status", "")).lower() == view.lower()]
    elif view in ["Approved", "Rejected"]:
        rows = [row for row in rows if str(row.get("Review", "")).lower() == view.lower()]
    if keyword:
        q = keyword.lower()
        rows = [row for row in rows if q in json.dumps(row, ensure_ascii=False).lower()]
    st.metric("Matching jobs", len(rows))
    if not rows:
        st.info("No matching jobs found.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open job JSON", [row["Path"] for row in rows]))
    data = read_json(selected, {})
    ok, messages = validate_job_record(data)
    st.success("Schema valid") if ok else st.warning("Schema warnings: " + "; ".join(messages))
    text = json_text(data)
    st.download_button("Download job JSON", data=text, file_name=selected.name, mime="application/json")
    st.json(data)


def render_image_gallery() -> None:
    st.header("Generated Images / Manifests")
    st.caption("Real generated images will appear here after Real Image Backend Phase 3.1. Placeholder manifests are already visible.")
    manifests = all_output_manifest_files()
    real_images = all_real_image_files()
    c1, c2 = st.columns(2)
    c1.metric("Placeholder manifests", len(manifests))
    c2.metric("Real image files", len(real_images))
    if real_images:
        st.markdown("### Real image gallery")
        cols = st.columns(3)
        for i, image_path in enumerate(real_images[:30]):
            with cols[i % 3]:
                st.image(str(image_path), caption=image_path.name, use_container_width=True)
                data = image_path.read_bytes()
                st.download_button("Download", data=data, file_name=image_path.name, mime="image/png", key=f"download_image_{i}")
    st.markdown("### Placeholder/output manifests")
    if not manifests:
        st.info("No output manifests found yet.")
        return
    rows = [{"File": p.name, "Modified": file_mtime(p), "Path": str(p)} for p in manifests]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open output manifest", [row["Path"] for row in rows]))
    data = read_json(selected, {})
    st.download_button("Download manifest JSON", data=json_text(data), file_name=selected.name, mime="application/json")
    st.json(data)


def render_bridge_control() -> None:
    st.header("Image Backend Control Panel")
    st.caption("Phase 2.20 controls the placeholder bridge. Real image backend controls will be connected in Phase 3.1.")
    limit = st.number_input("Max queued jobs to process", min_value=1, max_value=100, value=20, step=1)
    move_completed = st.checkbox("Copy completed job JSON to completed_jobs", value=False)
    queued = [row for row in all_image_job_rows() if row.get("Status") in ["created", "queued", "failed"]]
    st.metric("Processable jobs", len(queued))
    if queued:
        st.dataframe(queued, use_container_width=True, hide_index=True)
    if st.button("Process queued jobs with placeholder bridge", type="primary"):
        report = process_pending_jobs(limit=int(limit), move_completed=move_completed)
        st.success("Bridge run complete")
        st.json(report)
    st.markdown("### Real Image Backend Phase 3.1 placeholder")
    st.info("Stable Diffusion/Diffusers integration is not active yet. This panel is ready for the next backend adapter.")


def render_social_review() -> None:
    st.header("Social Review")
    c1, c2 = st.columns(2)
    if c1.button("Rebuild review queue", type="primary"):
        st.json(rebuild_review_queue())
    c2.info("Manual approval gate only. No real Facebook post happens from this tab.")
    queue = read_json(REVIEW_QUEUE_JSON, {"items": []})
    items = queue.get("items", []) if isinstance(queue, dict) else []
    st.metric("Review queue items", len(items))
    if not items:
        st.info("No review items found.")
        return
    rows = [{"Review ID": item.get("review_id", ""), "Project": item.get("project", ""), "Topic": item.get("topic", ""), "Status": item.get("status", ""), "Review": item.get("review_status", ""), "Output": item.get("output_path", ""), "Path": item.get("job_path", "")} for item in items]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected_path = st.selectbox("Select job", [row["Path"] for row in rows])
    selected_job = read_json(Path(selected_path), {})
    output_path = Path(str(selected_job.get("output_path", ""))) if isinstance(selected_job, dict) and selected_job.get("output_path") else None
    if output_path and output_path.exists():
        st.markdown("### Output preview")
        if output_path.suffix.lower() in IMAGE_EXTENSIONS:
            st.image(str(output_path), use_container_width=True)
        else:
            st.json(read_json(output_path, {}))
    note = st.text_input("Review note", value="manual review from Dashboard Phase 2.20")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("Approve selected"):
        st.success("Approved")
        st.json(set_review_status(Path(selected_path), "approved", note))
    if col_b.button("Reject selected"):
        st.warning("Rejected")
        st.json(set_review_status(Path(selected_path), "rejected", note))
    if col_c.button("Reset pending"):
        st.info("Reset to pending")
        st.json(set_review_status(Path(selected_path), "pending", note))
    st.markdown("### Selected job JSON")
    st.json(selected_job)


def render_approved_flow() -> None:
    st.header("Approved Flow")
    approved = read_json(APPROVED_JOBS_JSON, {"items": []})
    rejected = read_json(REJECTED_JOBS_JSON, {"items": []})
    approved_items_list = approved.get("items", []) if isinstance(approved, dict) else []
    rejected_items_list = rejected.get("items", []) if isinstance(rejected, dict) else []
    c1, c2 = st.columns(2)
    c1.metric("Approved", len(approved_items_list))
    c2.metric("Rejected", len(rejected_items_list))
    st.download_button("Download approved_jobs.json", data=json_text(approved), file_name="approved_jobs.json", mime="application/json")
    st.download_button("Download rejected_jobs.json", data=json_text(rejected), file_name="rejected_jobs.json", mime="application/json")
    st.markdown("### Approved jobs")
    st.json(approved)
    st.markdown("### Rejected jobs")
    st.json(rejected)


def render_health() -> None:
    st.header("Model / Backend Health")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Refresh model health", type="primary"):
            st.json(build_model_health())
        else:
            st.json(read_json(MODEL_HEALTH_JSON, {}) if MODEL_HEALTH_JSON.exists() else build_model_health())
    with col_b:
        st.json(build_health_summary())
    st.markdown("### Missing model helper")
    selected = st.multiselect("Models to pull", list(RECOMMENDED_MODELS.values()), default=[RECOMMENDED_MODELS["cpu_recommended"]])
    if st.button("Pull selected missing models"):
        st.json(pull_missing_models(selected))


def render_facebook_gate() -> None:
    st.header("Facebook Config / Manual Gate")
    config = ensure_config()
    st.warning("Safe default: disabled and dry-run. Real posting remains blocked unless explicitly enabled and manually confirmed.")
    with st.expander("Current Facebook config", expanded=True):
        st.json(config)
        st.code(str(FACEBOOK_CONFIG_JSON))
    items = approved_items()
    st.metric("Approved items available", len(items))
    if items:
        selected = st.selectbox("Approved item", [item.get("review_id") or item.get("job_id") for item in items])
        manual_confirm = st.checkbox("I manually reviewed and approve this gated attempt", value=False)
        if st.button("Run gated dry-run/post attempt"):
            st.json(gated_post_to_facebook(selected, manual_confirm=manual_confirm))
    log = read_json(SOCIAL_POST_LOG_JSON, {"items": []}) if SOCIAL_POST_LOG_JSON.exists() else {"items": []}
    st.markdown("### Social post log")
    st.json(log)


def render_final_package() -> None:
    st.header("Final Package Preview")
    approved = read_json(APPROVED_JOBS_JSON, {"items": []})
    items = approved.get("items", []) if isinstance(approved, dict) else []
    if not items:
        st.info("No approved packages yet. Approve a job first.")
        return
    selected = st.selectbox("Approved package", [item.get("review_id") or item.get("job_id") for item in items])
    item = next((entry for entry in items if (entry.get("review_id") or entry.get("job_id")) == selected), items[0])
    package = {
        "package_id": selected,
        "created_at": now_iso(),
        "project": item.get("project", ""),
        "topic": item.get("topic", ""),
        "job_path": item.get("job_path", ""),
        "output_path": item.get("output_path", ""),
        "prompt_preview": item.get("prompt_preview", ""),
        "posting_status": "manual_review_required",
        "facebook_real_posting": "disabled_by_default",
    }
    st.json(package)
    st.download_button("Download final package JSON", data=json_text(package), file_name=f"{selected}_package.json", mime="application/json")


def render_checklist() -> None:
    st.header("Final Frontend Checklist")
    items = [
        "Text Workstation UI cleanup status visible",
        "Dashboard 2.17/2.18/2.19 functionality unified in one app",
        "Navigation simplified",
        "Invalid old jobs filter available",
        "Generated Images / Manifests tab available",
        "Image preview gallery ready for real images",
        "Social Review output preview available",
        "Approved Flow polished with downloads",
        "Model and Backend Health combined",
        "One-click launcher status reflected in docs/runbook",
        "User-friendly status cards added",
        "Ready / Needs Action style status cards added",
        "Real Image Backend control panel placeholder added",
        "Image generation status view placeholder added",
        "Final Package Preview added",
        "Download buttons present",
        "Mobile-friendly wide layout and compact navigation used",
        "Final user checklist available in UI",
        "Old dashboard versions can remain as fallbacks",
        "Unified Dashboard Phase 2.20 ready",
    ]
    for item in items:
        st.checkbox(item, value=True, disabled=True)


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Dashboard")
    st.caption("Phase 2.20 — unified frontend: outputs, jobs, gallery, review, health, package preview")
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            [
                "Home",
                "Text Outputs",
                "Jobs",
                "Image Gallery",
                "Image Control",
                "Social Review",
                "Approved Flow",
                "Health",
                "Facebook Gate",
                "Final Package",
                "Checklist",
            ],
        )
        st.caption(f"Dashboard Phase {PHASE}")
    if page == "Home":
        render_home()
    elif page == "Text Outputs":
        render_text_outputs()
    elif page == "Jobs":
        render_jobs()
    elif page == "Image Gallery":
        render_image_gallery()
    elif page == "Image Control":
        render_bridge_control()
    elif page == "Social Review":
        render_social_review()
    elif page == "Approved Flow":
        render_approved_flow()
    elif page == "Health":
        render_health()
    elif page == "Facebook Gate":
        render_facebook_gate()
    elif page == "Final Package":
        render_final_package()
    elif page == "Checklist":
        render_checklist()


if __name__ == "__main__":
    main()
