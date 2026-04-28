"""Video placeholder backend adapter for Naz Lab.

This adapter creates a lightweight video manifest from a validated video package/job.
It does not render video, run FFmpeg, or use heavy video generation models.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.backend_status import mark_backend_failed, mark_backend_status  # noqa: E402
from shared.backend_validation import validate_backend_package  # noqa: E402
from shared.drive_paths import OUTPUT_LOG_JSON, VIDEO_OUTPUTS  # noqa: E402
from shared.json_utils import append_output_log, safe_read_json, safe_write_json  # noqa: E402


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "video_output"


def resolve_video_manifest_path(package: dict[str, Any], package_path: Path) -> Path:
    existing = str(package.get("video_output_path", package.get("suggested_output_path", ""))).strip()
    if existing:
        path = Path(existing)
        manifest = path.with_suffix(".txt")
        manifest.parent.mkdir(parents=True, exist_ok=True)
        return manifest

    VIDEO_OUTPUTS.mkdir(parents=True, exist_ok=True)
    project = safe_name(str(package.get("project_preset", "general")))
    title = safe_name(str(package.get("title", package_path.stem)))
    return VIDEO_OUTPUTS / f"placeholder_video_{project}_{title}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"


def validate_video_placeholder_rules(package: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    if not str(package.get("project_preset", "")).strip():
        messages.append("project_preset is required for video placeholder backend.")
    return messages


def create_video_manifest(package: dict[str, Any], manifest_path: Path) -> None:
    lines = [
        "Naz Lab Video Placeholder Manifest",
        "Generated: " + datetime.now().isoformat(timespec="seconds"),
        "",
        f"Project: {package.get('project_preset', '')}",
        f"Title: {package.get('title', '')}",
        f"Platform: {package.get('platform', 'Facebook Reels')}",
        f"Duration seconds: {package.get('duration_seconds', '')}",
        f"Voice path: {package.get('voice_path', package.get('audio_output_path', ''))}",
        f"Caption: {package.get('caption', '')}",
        "",
        "Scene list:",
        json.dumps(package.get("scene_list", package.get("scenes", [])), ensure_ascii=False, indent=2),
        "",
        "Image paths:",
        json.dumps(package.get("image_paths", []), ensure_ascii=False, indent=2),
        "",
        "This is not a final rendered video.",
        "Backend: video_placeholder_adapter",
    ]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(lines), encoding="utf-8")


def run_video_placeholder(package_path: Path, allow_draft: bool = False) -> dict[str, Any]:
    package = safe_read_json(package_path, {})
    if not isinstance(package, dict):
        return {"ok": False, "status": "blocked", "messages": ["Video package JSON must be an object."], "package_path": str(package_path)}

    backend_status = str(package.get("backend_status", package.get("status", "draft")))
    if backend_status != "ready_for_backend" and not allow_draft:
        return {
            "ok": False,
            "status": "blocked",
            "messages": ["Package backend_status must be ready_for_backend. Use --allow-draft only for manual testing."],
            "package_path": str(package_path),
        }

    validation = validate_backend_package(package, kind="video", source_path=package_path)
    rule_messages = validate_video_placeholder_rules(package)
    if not validation.ok or rule_messages:
        messages = list(validation.messages) + rule_messages
        try:
            mark_backend_failed(package_path, "; ".join(messages))
        except Exception:
            pass
        return {"ok": False, "status": "blocked", "messages": messages, "warnings": validation.warnings, "package_path": str(package_path)}

    manifest_path = resolve_video_manifest_path(package, package_path)
    try:
        mark_backend_status(package_path, "running", "Video placeholder backend started.", allow_any_transition=True)
        create_video_manifest(package, manifest_path)
        package = safe_read_json(package_path, {})
        if isinstance(package, dict):
            package["video_manifest_path"] = str(manifest_path)
            package["backend_adapter"] = "video_placeholder_adapter"
            package["backend_status"] = "completed"
            package["backend_last_updated"] = datetime.now().isoformat(timespec="seconds")
            package.setdefault("backend_events", [])
            package["backend_events"].append({"timestamp": datetime.now().isoformat(timespec="seconds"), "level": "info", "message": "Video placeholder manifest generated."})
            safe_write_json(package_path, package)
        append_output_log(
            OUTPUT_LOG_JSON,
            workstation="video_placeholder_backend",
            event="video_placeholder_generated",
            details={"package_path": str(package_path), "video_manifest_path": str(manifest_path), "adapter": "video_placeholder_adapter"},
        )
        return {"ok": True, "status": "completed", "video_manifest_path": str(manifest_path), "package_path": str(package_path)}
    except Exception as exc:
        try:
            mark_backend_failed(package_path, f"Video placeholder backend failed: {exc}")
        except Exception:
            pass
        return {"ok": False, "status": "failed", "messages": [str(exc)], "package_path": str(package_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a video placeholder manifest from a Naz Lab video package/job.")
    parser.add_argument("package_path", help="Path to a video backend package/job JSON file.")
    parser.add_argument("--allow-draft", action="store_true", help="Allow draft package status for manual testing.")
    args = parser.parse_args()
    result = run_video_placeholder(Path(args.package_path), allow_draft=args.allow_draft)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
