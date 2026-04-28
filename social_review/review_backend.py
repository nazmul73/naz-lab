"""Naz Lab Social Review backend.

Semi-automated review layer for jobs/packages before any social posting.
This does not post to Facebook. It only builds review records and approved jobs
JSON for later manual/API gated workflows.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, IMAGE_JOBS, LOGS_DIR  # noqa: E402
from shared.job_queue_schema import read_json, write_json  # noqa: E402

SOCIAL_REVIEW_DIR = BASE_PATH / "social_review"
REVIEW_QUEUE_JSON = SOCIAL_REVIEW_DIR / "review_queue.json"
APPROVED_JOBS_JSON = SOCIAL_REVIEW_DIR / "approved_jobs.json"
REJECTED_JOBS_JSON = SOCIAL_REVIEW_DIR / "rejected_jobs.json"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_dirs() -> None:
    SOCIAL_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    for path, default in [
        (REVIEW_QUEUE_JSON, {"items": []}),
        (APPROVED_JOBS_JSON, {"items": []}),
        (REJECTED_JOBS_JSON, {"items": []}),
    ]:
        if not path.exists():
            write_json(path, default)


def load_items(path: Path) -> list[dict[str, Any]]:
    data = read_json(path, {"items": []})
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return [item for item in data["items"] if isinstance(item, dict)]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def save_items(path: Path, items: list[dict[str, Any]]) -> None:
    write_json(path, {"updated_at": now_iso(), "items": items})


def review_record_from_job(job_path: Path) -> dict[str, Any] | None:
    job = read_json(job_path, {})
    if not isinstance(job, dict):
        return None
    payload = job.get("input_payload", {}) if isinstance(job.get("input_payload"), dict) else {}
    return {
        "review_id": f"review_{job.get('job_id', job_path.stem)}",
        "job_id": job.get("job_id", job_path.stem),
        "job_path": str(job_path),
        "project": job.get("project", ""),
        "topic": job.get("topic", ""),
        "status": job.get("status", "unknown"),
        "review_status": job.get("review_status", "pending"),
        "prompt_preview": str(payload.get("positive_prompt", job.get("prompt", "")))[:500],
        "output_path": job.get("output_path", ""),
        "created_at": job.get("created_at", ""),
        "updated_at": now_iso(),
    }


def rebuild_review_queue() -> dict[str, Any]:
    ensure_dirs()
    items: list[dict[str, Any]] = []
    for job_path in sorted(IMAGE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        record = review_record_from_job(job_path)
        if record:
            items.append(record)
    save_items(REVIEW_QUEUE_JSON, items)
    report = {"updated_at": now_iso(), "count": len(items), "review_queue_json": str(REVIEW_QUEUE_JSON)}
    write_json(LOGS_DIR / "social_review_last_rebuild.json", report)
    return report


def set_review_status(job_path: Path, review_status: str, note: str = "") -> dict[str, Any]:
    ensure_dirs()
    if review_status not in ["approved", "rejected", "pending"]:
        raise ValueError("review_status must be approved, rejected, or pending")
    job = read_json(job_path, {})
    if not isinstance(job, dict):
        raise ValueError(f"invalid job JSON: {job_path}")
    job["review_status"] = review_status
    job["updated_at"] = now_iso()
    job.setdefault("history", [])
    if isinstance(job["history"], list):
        job["history"].append({"at": now_iso(), "event": f"review_{review_status}", "by": "social_review_backend", "message": note})
    write_json(job_path, job)
    rebuild_review_queue()

    target = APPROVED_JOBS_JSON if review_status == "approved" else REJECTED_JOBS_JSON if review_status == "rejected" else REVIEW_QUEUE_JSON
    if review_status in ["approved", "rejected"]:
        items = load_items(target)
        record = review_record_from_job(job_path)
        if record:
            record["review_note"] = note
            items = [item for item in items if item.get("job_id") != record.get("job_id")]
            items.insert(0, record)
            save_items(target, items)
    return {"job_path": str(job_path), "review_status": review_status, "note": note}


if __name__ == "__main__":
    print(json.dumps(rebuild_review_queue(), ensure_ascii=False, indent=2))
