"""Generic TTS backend adapter skeleton for Naz Lab.

This adapter does not run a real TTS model yet. It validates a voice package and
prints the expected future TTS execution plan.
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


def build_tts_plan(package_path: Path) -> dict[str, object]:
    package = safe_read_json(package_path, {})
    if not isinstance(package, dict):
        return {
            "ok": False,
            "status": "blocked",
            "messages": ["Voice package JSON must be an object."],
            "package_path": str(package_path),
        }

    validation = validate_backend_package(package, kind="voice", source_path=package_path)
    return {
        "ok": validation.ok,
        "status": validation.status,
        "messages": validation.messages,
        "warnings": validation.warnings,
        "package_path": str(package_path),
        "backend_kind": "voice",
        "adapter": "generic_tts_adapter_skeleton",
        "will_run_generation": False,
        "future_inputs": {
            "language": package.get("language", ""),
            "voice_mode": package.get("voice_mode", ""),
            "tts_direction": package.get("tts_direction", ""),
            "script_draft": package.get("script_draft", ""),
            "audio_output_path": package.get("audio_output_path", package.get("suggested_audio_path", "")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Naz Lab voice package for future generic TTS backend use.")
    parser.add_argument("package_path", help="Path to a voice package JSON file.")
    args = parser.parse_args()
    plan = build_tts_plan(Path(args.package_path))
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
