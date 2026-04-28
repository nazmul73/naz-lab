"""Create a Naz Lab backend package from a lightweight template.

Usage from repo root:

    python backend_adapters/create_backend_package.py voice --project "General" --title "my test"

This script copies a backend template into the correct Drive package folder and
sets basic metadata. It does not run generation.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, IMAGE_JOBS, VIDEO_JOBS, VOICE_JOBS, FACE_JOBS  # noqa: E402
from shared.json_utils import safe_read_json, safe_write_json  # noqa: E402

TEMPLATE_DIR = REPO_ROOT / "backend_adapters" / "templates"

TEMPLATE_BY_KIND = {
    "voice": TEMPLATE_DIR / "voice_backend_package_template.json",
    "image": TEMPLATE_DIR / "image_backend_package_template.json",
    "video": TEMPLATE_DIR / "video_backend_package_template.json",
    "portrait": TEMPLATE_DIR / "portrait_backend_package_template.json",
}

OUTPUT_FOLDER_BY_KIND = {
    "voice": VOICE_JOBS,
    "image": IMAGE_JOBS,
    "video": VIDEO_JOBS,
    "portrait": FACE_JOBS,
}


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "backend_package"


def create_backend_package(kind: str, project: str, title: str, output_folder: str | None = None) -> Path:
    normalized = kind.strip().lower()
    if normalized not in TEMPLATE_BY_KIND:
        raise ValueError(f"Unsupported backend package kind: {kind}")

    template_path = TEMPLATE_BY_KIND[normalized]
    data = safe_read_json(template_path, {})
    if not isinstance(data, dict):
        raise ValueError(f"Template must be a JSON object: {template_path}")

    now = datetime.now().isoformat(timespec="seconds")
    data["created_at"] = now
    data["updated_at"] = now
    data["project_preset"] = project
    data["title"] = title
    data["backend_kind"] = normalized
    data["backend_status"] = "draft"
    data.setdefault("backend_events", [])
    data["backend_events"].append({"timestamp": now, "level": "info", "message": "Backend package created from template."})

    target_folder = Path(output_folder) if output_folder else OUTPUT_FOLDER_BY_KIND[normalized]
    target_folder.mkdir(parents=True, exist_ok=True)
    filename = f"backend_{normalized}_{safe_name(project)}_{safe_name(title)}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    target_path = target_folder / filename
    safe_write_json(target_path, data)
    return target_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Naz Lab backend package from a template.")
    parser.add_argument("kind", choices=sorted(TEMPLATE_BY_KIND), help="Backend package kind.")
    parser.add_argument("--project", default="General", help="Project preset name.")
    parser.add_argument("--title", default="backend package", help="Short package title.")
    parser.add_argument("--output-folder", default=None, help="Optional custom output folder.")
    args = parser.parse_args()

    path = create_backend_package(args.kind, args.project, args.title, args.output_folder)
    print(json.dumps({"ok": True, "path": str(path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
