"""Lightweight backend package status writer for Naz Lab.

Future backend adapters can use this module to safely mark packages as running,
completed, blocked, failed, or archived. It does not run generation.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from shared.backend_schema import BACKEND_PHASE, BACKEND_STATUS, STATUS_TRANSITIONS
from shared.json_utils import safe_read_json, safe_write_json


def can_transition(current_status: str, next_status: str) -> bool:
    """Return True if a backend status transition is allowed."""

    if current_status not in STATUS_TRANSITIONS:
        return False
    return next_status in STATUS_TRANSITIONS[current_status]


def backend_event(message: str, level: str = "info") -> dict[str, Any]:
    """Create a backend event entry."""

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "message": message,
    }


def mark_backend_status(
    package_path: str | Path,
    next_status: str,
    message: str,
    allow_any_transition: bool = False,
) -> dict[str, Any]:
    """Safely update backend status metadata inside a package JSON file."""

    path = Path(package_path)
    if next_status not in BACKEND_STATUS:
        raise ValueError(f"Unsupported backend status: {next_status}")

    data = safe_read_json(path, {})
    if not isinstance(data, dict):
        raise ValueError(f"Package JSON must be an object: {path}")

    current_status = str(data.get("backend_status", data.get("status", "draft")))
    if not allow_any_transition and not can_transition(current_status, next_status):
        raise ValueError(f"Invalid backend status transition: {current_status} -> {next_status}")

    data["backend_phase"] = BACKEND_PHASE
    data["backend_status"] = next_status
    data["backend_last_updated"] = datetime.now().isoformat(timespec="seconds")
    data.setdefault("backend_events", [])
    data["backend_events"].append(backend_event(message, level="info" if next_status != "failed" else "error"))

    safe_write_json(path, data)
    return data


def mark_backend_blocked(package_path: str | Path, message: str) -> dict[str, Any]:
    """Mark package as blocked, allowing transition from any status."""

    return mark_backend_status(package_path, "blocked", message, allow_any_transition=True)


def mark_backend_failed(package_path: str | Path, message: str) -> dict[str, Any]:
    """Mark package as failed, allowing transition from any status."""

    return mark_backend_status(package_path, "failed", message, allow_any_transition=True)


def mark_backend_ready(package_path: str | Path, message: str = "Package marked ready for backend.") -> dict[str, Any]:
    """Mark package as ready_for_backend, allowing transition from any status."""

    return mark_backend_status(package_path, "ready_for_backend", message, allow_any_transition=True)
