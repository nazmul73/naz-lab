"""Final reel pack assembler for Naz Lab.

This adapter creates a final reel pack JSON and Markdown manifest from existing
package/output files. It does not render video or run heavy generation tools.
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

from shared.drive_paths import BASE_PATH, IMAGE_OUTPUTS, OUTPUT_LOG_JSON, VIDEO_OUTPUTS  # noqa: E402
from shared.json_utils import append_output_log, safe_read_json, safe_write_json  # noqa: E402

AUDIO_OUTPUTS = BASE_PATH / "audio_outputs"
FINAL_REEL_PACKS = BASE_PATH / "final_reel_packs"
PROJECT_PACKAGES = BASE_PATH / "project_packages"
IMAGE_JOBS = BASE_PATH / "job_queue" / "image_jobs"
VOICE_JOBS = BASE_PATH / "job_queue" / "voice_jobs"
VIDEO_JOBS = BASE_PATH / "job_queue" / "video_jobs"


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "final_reel_pack"


def latest_files(folder: Path, suffixes: set[str], limit: int = 5) -> list[Path]:
    if not folder.exists():
        return []
    files = [path for path in folder.glob("*") if path.is_file() and path.suffix.lower() in suffixes]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def latest_json(folder: Path, limit: int = 5) -> list[Path]:
    return latest_files(folder, {".json"}, limit=limit)


def read_json_summary(path: Path) -> dict[str, Any]:
    data = safe_read_json(path, {})
    if not isinstance(data, dict):
        return {"path": str(path), "file": path.name, "status": "unreadable"}
    return {
        "path": str(path),
        "file": path.name,
        "project_preset": data.get("project_preset", data.get("visual_preset", "")),
        "title": data.get("title", data.get("topic", "")),
        "language": data.get("language", ""),
        "status": data.get("backend_status", data.get("status", "")),
        "audio_output_path": data.get("audio_output_path", ""),
        "image_output_path": data.get("image_output_path", data.get("suggested_output_path", "")),
        "video_manifest_path": data.get("video_manifest_path", ""),
    }


def first_existing_path(paths: list[str]) -> str:
    for path_text in paths:
        if path_text and Path(path_text).exists():
            return path_text
    for path_text in paths:
        if path_text:
            return path_text
    return ""


def build_final_pack(project: str, title: str, limit: int = 5) -> tuple[dict[str, Any], str]:
    project_packages = latest_json(PROJECT_PACKAGES, limit=limit)
    image_jobs = latest_json(IMAGE_JOBS, limit=limit)
    voice_jobs = latest_json(VOICE_JOBS, limit=limit)
    video_jobs = latest_json(VIDEO_JOBS, limit=limit)
    images = latest_files(IMAGE_OUTPUTS, {".png", ".jpg", ".jpeg", ".webp"}, limit=limit)
    audio = latest_files(AUDIO_OUTPUTS, {".mp3", ".wav", ".m4a"}, limit=limit)
    video_manifests = latest_files(VIDEO_OUTPUTS, {".txt", ".json", ".md", ".mp4"}, limit=limit)

    source_summaries = [read_json_summary(path) for path in project_packages + image_jobs + voice_jobs + video_jobs]
    audio_candidates = [summary.get("audio_output_path", "") for summary in source_summaries] + [str(path) for path in audio]
    image_candidates = [summary.get("image_output_path", "") for summary in source_summaries] + [str(path) for path in images]
    video_candidates = [summary.get("video_manifest_path", "") for summary in source_summaries] + [str(path) for path in video_manifests]

    warnings: list[str] = []
    if not image_candidates:
        warnings.append("No image outputs found.")
    if not audio_candidates:
        warnings.append("No audio outputs found.")
    if not video_candidates:
        warnings.append("No video manifest/output found.")

    pack = {
        "phase": "Final Reel Pack Assembly 1.0",
        "status": "assembled",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project_preset": project,
        "title": title,
        "language": "Bangla",
        "script_text": "",
        "caption": "",
        "hashtags": [],
        "image_paths": [path for path in image_candidates if path][:limit],
        "audio_path": first_existing_path(audio_candidates),
        "video_manifest_path": first_existing_path(video_candidates),
        "source_packages": source_summaries,
        "warnings": warnings,
        "safety_notes": [
            "Final Reel Pack Assembly does not render final video.",
            "Reference voice/image policy metadata should remain in source packages.",
            "Bangla-first content direction should be preserved.",
        ],
    }
    markdown = pack_to_markdown(pack)
    return pack, markdown


def pack_to_markdown(pack: dict[str, Any]) -> str:
    lines = [
        f"# Final Reel Pack: {pack.get('title', '')}",
        "",
        f"Project: {pack.get('project_preset', '')}",
        f"Status: {pack.get('status', '')}",
        f"Created: {pack.get('created_at', '')}",
        "",
        "## Outputs",
        f"- Audio: `{pack.get('audio_path', '')}`",
        f"- Video manifest: `{pack.get('video_manifest_path', '')}`",
        "- Images:",
    ]
    for path in pack.get("image_paths", []):
        lines.append(f"  - `{path}`")
    lines.extend(["", "## Warnings"])
    warnings = pack.get("warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No warnings.")
    lines.extend(["", "## Source packages"])
    for source in pack.get("source_packages", []):
        lines.append(f"- `{source.get('path', '')}` — {source.get('status', '')}")
    lines.extend(["", "## Safety notes"])
    for note in pack.get("safety_notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines)


def assemble_final_reel_pack(project: str, title: str, limit: int = 5) -> dict[str, Any]:
    FINAL_REEL_PACKS.mkdir(parents=True, exist_ok=True)
    pack, markdown = build_final_pack(project=project, title=title, limit=limit)
    stem = f"final_reel_pack_{safe_name(project)}_{safe_name(title)}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    json_path = FINAL_REEL_PACKS / f"{stem}.json"
    markdown_path = FINAL_REEL_PACKS / f"{stem}.md"
    safe_write_json(json_path, pack)
    markdown_path.write_text(markdown, encoding="utf-8")
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="final_reel_pack_assembler",
        event="final_reel_pack_assembled",
        details={"json_path": str(json_path), "markdown_path": str(markdown_path), "project": project, "title": title},
    )
    return {"ok": True, "status": "assembled", "json_path": str(json_path), "markdown_path": str(markdown_path), "warnings": pack.get("warnings", [])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble a Naz Lab final reel pack manifest from existing outputs.")
    parser.add_argument("--project", default="General", help="Project preset name.")
    parser.add_argument("--title", default="final reel pack", help="Final reel pack title.")
    parser.add_argument("--limit", type=int, default=5, help="Latest files per source folder to include.")
    args = parser.parse_args()
    result = assemble_final_reel_pack(args.project, args.title, args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
