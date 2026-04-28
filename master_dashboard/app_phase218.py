"""Naz Lab Master Dashboard Phase 2.18.

Adds backend/frontend coverage for items 11-20:
- failed/approved job views
- image bridge controls
- social review approve/reject UI
- approved jobs JSON flow
- backend health summary JSON
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
from shared.drive_paths import BASE_PATH, IMAGE_JOBS, IMAGE_OUTPUTS, LOGS_DIR, WORKSTATION_LINKS_JSON  # noqa: E402
from shared.job_queue_schema import read_json, summarize_job_file, validate_job_record, write_json  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402
from social_review.review_backend import (  # noqa: E402
    APPROVED_JOBS_JSON,
    REJECTED_JOBS_JSON,
    REVIEW_QUEUE_JSON,
    rebuild_review_queue,
    set_review_status,
)

PHASE = "2.18"
PHASE_STATUS = "review-bridge-health-ready"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def latest_jobs(limit: int = 1000) -> list[Path]:
    if not IMAGE_JOBS.exists():
        return []
    return sorted(IMAGE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rows_by_status(statuses: list[str] | None = None, review: str | None = None) -> list[dict[str, Any]]:
    rows = [summarize_job_file(path) for path in latest_jobs()]
    if statuses is not None:
        rows = [row for row in rows if row.get("Status") in statuses]
    if review is not None:
        rows = [row for row in rows if row.get("Review") == review]
    return rows


def render_status() -> None:
    st.header("Backend health summary")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": now_iso()})
    if st.button("Refresh health summary", type="primary"):
        summary = build_health_summary()
        st.success(f"Health summary written to {LOGS_DIR / 'backend_health_summary.json'}")
        st.json(summary)
    else:
        summary_path = LOGS_DIR / "backend_health_summary.json"
        summary = read_json(summary_path, {}) if summary_path.exists() else build_health_summary()
        st.json(summary)
    st.download_button("Download backend health JSON", data=json.dumps(summary, ensure_ascii=False, indent=2), file_name="backend_health_summary.json", mime="application/json")


def render_failed_approved() -> None:
    st.header("Failed / Approved Job View")
    c1, c2, c3 = st.columns(3)
    failed = rows_by_status(["failed"])
    done = rows_by_status(["done"])
    approved = rows_by_status(review="approved")
    c1.metric("Failed", len(failed))
    c2.metric("Done", len(done))
    c3.metric("Approved", len(approved))
    view = st.radio("View", ["Failed", "Done", "Approved", "Rejected"], horizontal=True)
    if view == "Failed":
        rows = failed
    elif view == "Done":
        rows = done
    elif view == "Approved":
        rows = approved
    else:
        rows = rows_by_status(review="rejected")
    if not rows:
        st.info(f"No {view.lower()} jobs found.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = Path(st.selectbox("Open job", [row["Path"] for row in rows]))
    data = read_json(selected, {})
    st.json(data)
    st.download_button("Download selected job JSON", data=json.dumps(data, ensure_ascii=False, indent=2), file_name=selected.name, mime="application/json")


def render_image_bridge() -> None:
    st.header("Image Workstation Bridge")
    st.caption("Creates placeholder output manifests and updates queued jobs to done/failed. No heavy image generation runs here.")
    limit = st.number_input("Max jobs to process", min_value=1, max_value=100, value=20, step=1)
    move_completed = st.checkbox("Copy completed job JSON to completed_jobs", value=False)
    queued = rows_by_status(["created", "queued", "failed"])
    st.metric("Processable jobs", len(queued))
    if queued:
        st.dataframe(queued, use_container_width=True, hide_index=True)
    if st.button("Process pending image jobs", type="primary"):
        report = process_pending_jobs(limit=int(limit), move_completed=move_completed)
        st.success("Bridge run complete")
        st.json(report)
    output_files = sorted(IMAGE_OUTPUTS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:100] if IMAGE_OUTPUTS.exists() else []
    st.markdown("### Placeholder outputs")
    if output_files:
        st.dataframe([{"File": p.name, "Modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "Path": str(p)} for p in output_files], use_container_width=True, hide_index=True)
    else:
        st.info("No placeholder image output manifests yet.")


def render_social_review() -> None:
    st.header("Social Review")
    c1, c2 = st.columns(2)
    if c1.button("Rebuild review queue", type="primary"):
        report = rebuild_review_queue()
        st.success("Review queue rebuilt")
        st.json(report)
    c2.caption("This does not post to Facebook. It only gates approved jobs JSON.")

    queue = read_json(REVIEW_QUEUE_JSON, {"items": []})
    items = queue.get("items", []) if isinstance(queue, dict) else []
    st.metric("Review queue items", len(items))
    if not items:
        st.info("No review items yet. Create image jobs first, then rebuild review queue.")
        return
    rows = [{"Review ID": item.get("review_id", ""), "Project": item.get("project", ""), "Topic": item.get("topic", ""), "Job status": item.get("status", ""), "Review": item.get("review_status", ""), "Path": item.get("job_path", "")} for item in items]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected_path = st.selectbox("Select job for review", [row["Path"] for row in rows])
    note = st.text_input("Review note", value="manual review from Dashboard Phase 2.18")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("Approve selected"):
        result = set_review_status(Path(selected_path), "approved", note)
        st.success("Approved")
        st.json(result)
    if col_b.button("Reject selected"):
        result = set_review_status(Path(selected_path), "rejected", note)
        st.warning("Rejected")
        st.json(result)
    if col_c.button("Reset to pending"):
        result = set_review_status(Path(selected_path), "pending", note)
        st.info("Reset to pending")
        st.json(result)
    data = read_json(Path(selected_path), {})
    ok, messages = validate_job_record(data)
    st.markdown("### Selected job")
    st.success("Schema valid") if ok else st.warning("Schema warnings: " + "; ".join(messages))
    st.json(data)


def render_approved_flow() -> None:
    st.header("Approved Jobs JSON Flow")
    approved = read_json(APPROVED_JOBS_JSON, {"items": []})
    rejected = read_json(REJECTED_JOBS_JSON, {"items": []})
    review = read_json(REVIEW_QUEUE_JSON, {"items": []})
    c1, c2, c3 = st.columns(3)
    c1.metric("Review queue", len(review.get("items", [])) if isinstance(review, dict) else 0)
    c2.metric("Approved", len(approved.get("items", [])) if isinstance(approved, dict) else 0)
    c3.metric("Rejected", len(rejected.get("items", [])) if isinstance(rejected, dict) else 0)
    st.markdown("### Approved jobs")
    st.json(approved)
    st.download_button("Download approved_jobs.json", data=json.dumps(approved, ensure_ascii=False, indent=2), file_name="approved_jobs.json", mime="application/json")
    st.markdown("### Rejected jobs")
    st.json(rejected)
    st.download_button("Download rejected_jobs.json", data=json.dumps(rejected, ensure_ascii=False, indent=2), file_name="rejected_jobs.json", mime="application/json")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Dashboard")
    st.caption("Phase 2.18 — failed/approved jobs, image bridge, social review, approved jobs flow, backend health summary")
    tabs = st.tabs(["Health", "Failed / Approved", "Image Bridge", "Social Review", "Approved Flow"])
    with tabs[0]:
        render_status()
    with tabs[1]:
        render_failed_approved()
    with tabs[2]:
        render_image_bridge()
    with tabs[3]:
        render_social_review()
    with tabs[4]:
        render_approved_flow()


if __name__ == "__main__":
    main()
