"""Video backend adapter skeleton for Naz Lab.

This adapter does not run FFmpeg, image-to-video models, or any heavy video
backend. It validates a video package JSON and prints a future execution plan.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.backend_validation import validate_backend_package  # noqa: E402
from shared.json_utils import safe_read_json  # noqa: E402


def build_video_plan(package_path: Path) -> dict[str, object]:
    package = safe_read_json(package_path, {})
    if not isinstance(package, dict):
        return {
            "ok": False,
            "status": "blocked",
            "messages": ["Video package JSON must be an object."],
            "package_path": str(package_path),
        }

    validation = validate_backend_package(package, kind="video", source_path=package_path)
    return {
        "ok": validation.ok,
        "status": validation.status,
        "messages": validation.messages,
        "warnings": validation.warnings,
        "package_path": str(package_path),
        "backend_kind": "video",
        "adapter": "video_adapter_skeleton",
        "will_run_generation": False,
        "future_inputs": {
            "project_preset": package.get("project_preset", ""),
            "scene_list": package.get("scene_list", package.get("scenes", [])),
            "image_paths": package.get("image_paths", []),
            "voice_path": package.get("voice_path", package.get("audio_output_path", "")),
            "caption": package.get("caption", ""),
            "platform": package.get("platform", "Facebook Reels"),
            "suggested_output_path": package.get("suggested_output_path", package.get("video_output_path", "")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Naz Lab video package for future video backend use.")
    parser.add_argument("package_path", help="Path to a video package JSON file.")
    args = parser.parse_args()
    plan = build_video_plan(Path(args.package_path))
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
