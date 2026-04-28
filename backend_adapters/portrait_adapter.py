"""Portrait backend adapter skeleton for Naz Lab.

This adapter does not run LivePortrait, FaceFusion, or any heavy portrait/face
backend. It validates a portrait package JSON and prints a future execution plan.
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


def build_portrait_plan(package_path: Path) -> dict[str, object]:
    package = safe_read_json(package_path, {})
    if not isinstance(package, dict):
        return {
            "ok": False,
            "status": "blocked",
            "messages": ["Portrait package JSON must be an object."],
            "package_path": str(package_path),
        }

    validation = validate_backend_package(package, kind="portrait", source_path=package_path)
    return {
        "ok": validation.ok,
        "status": validation.status,
        "messages": validation.messages,
        "warnings": validation.warnings,
        "package_path": str(package_path),
        "backend_kind": "portrait",
        "adapter": "portrait_adapter_skeleton",
        "will_run_generation": False,
        "future_inputs": {
            "project_preset": package.get("project_preset", ""),
            "portrait_type": package.get("portrait_type", ""),
            "positive_prompt": package.get("positive_prompt", ""),
            "negative_prompt": package.get("negative_prompt", ""),
            "reference_image_path": package.get("reference_image_path", ""),
            "reference_image_authorized": package.get("reference_image_authorized", False),
            "no_misleading_identity_claim": package.get("no_misleading_identity_claim", False),
            "suggested_output_path": package.get("suggested_output_path", package.get("portrait_output_path", "")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Naz Lab portrait package for future portrait backend use.")
    parser.add_argument("package_path", help="Path to a portrait package JSON file.")
    args = parser.parse_args()
    plan = build_portrait_plan(Path(args.package_path))
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
