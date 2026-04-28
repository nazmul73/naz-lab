"""Lightweight backend queue scanner for Naz Lab.

This scanner reads existing package/job JSON files and reports whether they are
ready, blocked, or warning-only for future backend adapters. It never runs heavy
AI generation.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from shared.backend_schema import infer_backend_kind_from_path
from shared.backend_validation import validate_backend_package
from shared.drive_paths import IMAGE_JOBS, VOICE_JOBS, VIDEO_JOBS, FACE_JOBS, BASE_PATH
from shared.json_utils import safe_read_json

PROJECT_PACKAGES = BASE_PATH / "project_packages"
VOICE_PACKAGES = BASE_PATH / "voice_packages"
VOICE_CLONE_PACKAGES = BASE_PATH / "voice_clone_packages"
VIDEO_PACKAGES = BASE_PATH / "video_packages"
PORTRAIT_PACKAGES = BASE_PATH / "portrait_packages"

BACKEND_SCAN_FOLDERS = {
    "image": [IMAGE_JOBS],
    "voice": [VOICE_JOBS, VOICE_PACKAGES, VOICE_CLONE_PACKAGES],
    "video": [VIDEO_JOBS, VIDEO_PACKAGES],
    "portrait": [FACE_JOBS, PORTRAIT_PACKAGES],
    "project": [PROJECT_PACKAGES],
}


def list_json_files(folder: Path, limit: int = 100) -> list[Path]:
    """Return latest JSON files from a folder."""

    if not folder.exists():
        return []
    files = [path for path in folder.glob("*.json") if path.is_file()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def scan_backend_folder(kind: str, folder: Path, limit: int = 100) -> list[dict[str, Any]]:
    """Scan one backend folder and return validation summaries."""

    rows: list[dict[str, Any]] = []
    for path in list_json_files(folder, limit=limit):
        data = safe_read_json(path, {})
        if not isinstance(data, dict):
            rows.append(
                {
                    "path": str(path),
                    "file": path.name,
                    "folder": path.parent.name,
                    "kind": kind,
                    "ok": False,
                    "status": "blocked",
                    "messages": ["Package JSON is not an object."],
                    "warnings": [],
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                }
            )
            continue
        inferred_kind = kind if kind != "project" else infer_backend_kind_from_path(path)
        result = validate_backend_package(data, kind=inferred_kind, source_path=path)
        rows.append(
            {
                "path": str(path),
                "file": path.name,
                "folder": path.parent.name,
                "kind": inferred_kind,
                "project": data.get("project_preset", data.get("visual_preset", "")),
                "status": data.get("backend_status", data.get("status", "draft")),
                "ok": result.ok,
                "validation_status": result.status,
                "messages": result.messages,
                "warnings": result.warnings,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            }
        )
    return rows


def scan_backend_queues(limit_per_folder: int = 100) -> dict[str, Any]:
    """Scan all known backend queue/package folders."""

    report: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "folders": {},
        "summary": {"total": 0, "ready": 0, "blocked": 0, "warning_only": 0},
    }

    for kind, folders in BACKEND_SCAN_FOLDERS.items():
        kind_rows: list[dict[str, Any]] = []
        for folder in folders:
            rows = scan_backend_folder(kind, folder, limit=limit_per_folder)
            kind_rows.extend(rows)
        report["folders"][kind] = kind_rows

    all_rows = [row for rows in report["folders"].values() for row in rows]
    report["summary"]["total"] = len(all_rows)
    report["summary"]["ready"] = sum(1 for row in all_rows if row.get("ok") is True)
    report["summary"]["blocked"] = sum(1 for row in all_rows if row.get("ok") is False)
    report["summary"]["warning_only"] = sum(1 for row in all_rows if row.get("ok") is True and row.get("warnings"))
    return report
