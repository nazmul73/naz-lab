"""Naz Lab shared Job Queue schema utilities.

This module standardizes JSON job records used to connect workstations.
It is intentionally lightweight and safe for Colab/Streamlit runtimes.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.10"
VALID_JOB_STATUSES = ["created", "queued", "processing", "done", "failed", "approved", "rejected"]
VALID_REVIEW_STATUSES = ["pending", "approved", "rejected"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def make_job_id(prefix: str = "job") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def normalize_status(status: str | None, default: str = "queued") -> str:
    value = str(status or default).strip().lower()
    if value == "pending":
        return "queued"
    if value not in VALID_JOB_STATUSES:
        return default
    return value


def image_job_record(
    *,
    project: str,
    topic: str,
    prompt: str,
    source_workstation: str = "text_workstation",
    source_mode: str = "Prompt Improver",
    source_text_path: str = "",
    negative_prompt: str = "no fake logo, no watermark, no distorted face",
) -> dict[str, Any]:
    job_id = make_job_id("image")
    created = now_iso()
    return {
        "job_id": job_id,
        "schema_version": SCHEMA_VERSION,
        "source_workstation": source_workstation,
        "target_workstation": "image_workstation",
        "source_mode": source_mode,
        "project": project,
        "topic": topic,
        "status": "queued",
        "review_status": "pending",
        "created_at": created,
        "updated_at": created,
        "input_payload": {
            "positive_prompt": prompt,
            "negative_prompt": negative_prompt,
            "format": "1:1 square by default; adapt to 9:16 for reels when requested",
        },
        "source_text_path": source_text_path,
        "output_path": "",
        "errors": [],
        "history": [
            {"at": created, "event": "created", "by": source_workstation},
            {"at": created, "event": "queued", "by": source_workstation},
        ],
    }


def validate_job_record(data: Any) -> tuple[bool, list[str]]:
    messages: list[str] = []
    if not isinstance(data, dict):
        return False, ["job JSON must be an object"]
    required = ["job_id", "schema_version", "source_workstation", "target_workstation", "status", "created_at", "updated_at", "input_payload", "errors"]
    for key in required:
        if key not in data:
            messages.append(f"missing required field: {key}")
    status = normalize_status(data.get("status"), default="queued")
    if status != data.get("status") and data.get("status") not in [None, "pending"]:
        messages.append(f"invalid status: {data.get('status')}")
    review_status = data.get("review_status", "pending")
    if review_status not in VALID_REVIEW_STATUSES:
        messages.append(f"invalid review_status: {review_status}")
    if not isinstance(data.get("errors", []), list):
        messages.append("errors must be a list")
    if not isinstance(data.get("input_payload", {}), dict):
        messages.append("input_payload must be an object")
    return not messages, messages


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_job_file(path: Path) -> dict[str, Any]:
    data = read_json(path, {})
    ok, messages = validate_job_record(data)
    payload = data.get("input_payload", {}) if isinstance(data, dict) else {}
    prompt = payload.get("positive_prompt", data.get("prompt", "")) if isinstance(payload, dict) and isinstance(data, dict) else ""
    return {
        "File": path.name,
        "Project": data.get("project", "") if isinstance(data, dict) else "",
        "Topic": str(data.get("topic", ""))[:120] if isinstance(data, dict) else "",
        "Status": data.get("status", "unknown") if isinstance(data, dict) else "invalid",
        "Review": data.get("review_status", "pending") if isinstance(data, dict) else "invalid",
        "Source": data.get("source_workstation", "") if isinstance(data, dict) else "",
        "Target": data.get("target_workstation", "") if isinstance(data, dict) else "",
        "Prompt": str(prompt)[:160],
        "Valid": ok,
        "Messages": "; ".join(messages),
        "Modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "Path": str(path),
    }
