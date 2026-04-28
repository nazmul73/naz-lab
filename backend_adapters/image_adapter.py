"""Image backend adapter skeleton for Naz Lab.

This adapter does not run Fooocus, Stable Diffusion, SDXL, or any heavy model.
It validates an image package/job JSON and prints the expected future execution
plan.
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


def build_image_plan(package_path: Path) -> dict[str, object]:
    package = safe_read_json(package_path, {})
    if not isinstance(package, dict):
        return {
            "ok": False,
            "status": "blocked",
            "messages": ["Image package/job JSON must be an object."],
            "package_path": str(package_path),
        }

    validation = validate_backend_package(package, kind="image", source_path=package_path)
    return {
        "ok": validation.ok,
        "status": validation.status,
        "messages": validation.messages,
        "warnings": validation.warnings,
        "package_path": str(package_path),
        "backend_kind": "image",
        "adapter": "image_adapter_skeleton",
        "will_run_generation": False,
        "future_inputs": {
            "project_preset": package.get("project_preset", package.get("visual_preset", "")),
            "positive_prompt": package.get("positive_prompt", package.get("prompt", "")),
            "negative_prompt": package.get("negative_prompt", ""),
            "output_format": package.get("output_format", ""),
            "suggested_output_path": package.get("suggested_output_path", package.get("image_output_path", "")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Naz Lab image package/job for future image backend use.")
    parser.add_argument("package_path", help="Path to an image package/job JSON file.")
    args = parser.parse_args()
    plan = build_image_plan(Path(args.package_path))
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
