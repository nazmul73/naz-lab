"""Naz Lab Image Workstation Bridge Phase 1.

Lightweight backend bridge for job lifecycle testing.
It watches/reads image job JSON files, validates the shared schema, creates a
placeholder output manifest, and updates job status without running heavy image
generation.

Real Stable Diffusion/Fooocus integration remains a future adapter hook.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import COMPLETED_JOBS, IMAGE_JOBS, IMAGE_OUTPUTS, LOGS_DIR  # noqa: E402
from shared.job_queue_schema import read_json, validate_job_record, write_json  # noqa: E402

BRIDGE_VERSION = "image-bridge-1.0"
STATUS_FLOW = ["queued", "processing", "done", "failed"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_dirs() -> None:
    for folder in [IMAGE_JOBS, IMAGE_OUTPUTS, COMPLETED_JOBS, LOGS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def append_history(job: dict[str, Any], event: str, message: str = "") -> None:
    history = job.setdefault("history", [])
    if isinstance(history, list):
        history.append({"at": now_iso(), "event": event, "by": BRIDGE_VERSION, "message": message})


def set_status(job: dict[str, Any], status: str, message: str = "") -> None:
    job["status"] = status
    job["updated_at"] = now_iso()
    append_history(job, status, message)


def placeholder_output(job: dict[str, Any], job_path: Path) -> Path:
    job_id = str(job.get("job_id", job_path.stem))
    output_path = IMAGE_OUTPUTS / f"{job_id}_placeholder_manifest.json"
    payload = job.get("input_payload", {}) if isinstance(job.get("input_payload"), dict) else {}
    manifest = {
        "bridge_version": BRIDGE_VERSION,
        "created_at": now_iso(),
        "job_id": job_id,
        "source_job_path": str(job_path),
        "project": job.get("project", ""),
        "topic": job.get("topic", ""),
        "positive_prompt": payload.get("positive_prompt", job.get("prompt", "")),
        "negative_prompt": payload.get("negative_prompt", "no fake logo, no watermark, no distorted face"),
        "status": "placeholder_done",
        "note": "Placeholder manifest only. Real image generation is deferred to a future image backend adapter.",
    }
    write_json(output_path, manifest)
    return output_path


def process_job(job_path: Path, *, move_completed: bool = False) -> dict[str, Any]:
    ensure_dirs()
    job = read_json(job_path, {})
    if not isinstance(job, dict):
        return {"path": str(job_path), "ok": False, "status": "failed", "message": "job file is not valid JSON object"}

    ok, messages = validate_job_record(job)
    if not ok:
        job.setdefault("errors", [])
        if isinstance(job["errors"], list):
            job["errors"].extend(messages)
        set_status(job, "failed", "schema validation failed")
        write_json(job_path, job)
        return {"path": str(job_path), "ok": False, "status": "failed", "message": "; ".join(messages)}

    status = str(job.get("status", "queued"))
    if status not in ["created", "queued", "failed"]:
        return {"path": str(job_path), "ok": True, "status": status, "message": "skipped non-queued job"}

    try:
        set_status(job, "processing", "bridge picked up job")
        write_json(job_path, job)
        output_path = placeholder_output(job, job_path)
        job["output_path"] = str(output_path)
        set_status(job, "done", "placeholder output manifest created")
        write_json(job_path, job)
        completed_copy = ""
        if move_completed:
            completed_path = COMPLETED_JOBS / job_path.name
            shutil.copy2(job_path, completed_path)
            completed_copy = str(completed_path)
        return {"path": str(job_path), "ok": True, "status": "done", "output_path": str(output_path), "completed_copy": completed_copy}
    except Exception as exc:
        job.setdefault("errors", [])
        if isinstance(job["errors"], list):
            job["errors"].append(str(exc))
        set_status(job, "failed", str(exc))
        write_json(job_path, job)
        return {"path": str(job_path), "ok": False, "status": "failed", "message": str(exc)}


def process_pending_jobs(limit: int = 20, *, move_completed: bool = False) -> dict[str, Any]:
    ensure_dirs()
    job_files = sorted(IMAGE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime)[:limit]
    results = [process_job(path, move_completed=move_completed) for path in job_files]
    report = {"bridge_version": BRIDGE_VERSION, "created_at": now_iso(), "processed": results}
    write_json(LOGS_DIR / "image_bridge_last_run.json", report)
    return report


if __name__ == "__main__":
    print(json.dumps(process_pending_jobs(), ensure_ascii=False, indent=2))
