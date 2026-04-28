"""Naz Lab backend health summary utility."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, IMAGE_JOBS, IMAGE_OUTPUTS, LOGS_DIR, TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS  # noqa: E402
from shared.job_queue_schema import summarize_job_file, write_json  # noqa: E402

SOCIAL_REVIEW_DIR = BASE_PATH / "social_review"
REVIEW_QUEUE_JSON = SOCIAL_REVIEW_DIR / "review_queue.json"
APPROVED_JOBS_JSON = SOCIAL_REVIEW_DIR / "approved_jobs.json"
REJECTED_JOBS_JSON = SOCIAL_REVIEW_DIR / "rejected_jobs.json"
HEALTH_JSON = LOGS_DIR / "backend_health_summary.json"


def count_files(folder: Path, pattern: str = "*") -> int:
    if not folder.exists():
        return 0
    return sum(1 for item in folder.rglob(pattern) if item.is_file())


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def social_count(path: Path) -> int:
    data = read_json(path, {"items": []})
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return len(data["items"])
    if isinstance(data, list):
        return len(data)
    return 0


def build_health_summary() -> dict[str, Any]:
    jobs = [summarize_job_file(path) for path in IMAGE_JOBS.glob("*.json")] if IMAGE_JOBS.exists() else []
    by_status: dict[str, int] = {}
    invalid = 0
    for row in jobs:
        status = str(row.get("Status", "unknown"))
        by_status[status] = by_status.get(status, 0) + 1
        if not row.get("Valid"):
            invalid += 1
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base_path": str(BASE_PATH),
        "folders": {
            "text_outputs": {"path": str(TEXT_OUTPUTS), "files": count_files(TEXT_OUTPUTS, "*.txt")},
            "script_outputs": {"path": str(SCRIPT_OUTPUTS), "files": count_files(SCRIPT_OUTPUTS, "*.txt")},
            "image_prompts": {"path": str(IMAGE_PROMPTS), "files": count_files(IMAGE_PROMPTS, "*.txt")},
            "image_jobs": {"path": str(IMAGE_JOBS), "files": count_files(IMAGE_JOBS, "*.json")},
            "image_outputs": {"path": str(IMAGE_OUTPUTS), "files": count_files(IMAGE_OUTPUTS, "*.json")},
            "social_review": {"path": str(SOCIAL_REVIEW_DIR), "files": count_files(SOCIAL_REVIEW_DIR, "*.json")},
        },
        "image_jobs_by_status": by_status,
        "invalid_image_jobs": invalid,
        "social_review": {
            "pending_or_all": social_count(REVIEW_QUEUE_JSON),
            "approved": social_count(APPROVED_JOBS_JSON),
            "rejected": social_count(REJECTED_JOBS_JSON),
            "review_queue_json": str(REVIEW_QUEUE_JSON),
            "approved_jobs_json": str(APPROVED_JOBS_JSON),
            "rejected_jobs_json": str(REJECTED_JOBS_JSON),
        },
    }
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    write_json(HEALTH_JSON, summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(build_health_summary(), ensure_ascii=False, indent=2))
