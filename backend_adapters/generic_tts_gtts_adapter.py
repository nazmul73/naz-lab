"""gTTS generic TTS backend adapter for Naz Lab.

This is the first lightweight real backend adapter. It generates generic TTS
MP3 audio from a validated voice package. It does not clone voices and blocks
reference voice clone mode.
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
from shared.drive_paths import AUDIO_OUTPUTS, OUTPUT_LOG_JSON  # noqa: E402
from shared.json_utils import append_output_log, safe_read_json, safe_write_json  # noqa: E402

BLOCKED_VOICE_MODES = {"authorized reference voice clone planning"}
TEXT_FIELDS = ["script_draft", "voiceover_text", "text", "combined_package"]
LANGUAGE_CODE_BY_NAME = {
    "bangla": "bn",
    "bengali": "bn",
    "english": "en",
    "mixed english-bangla": "bn",
    "mixed bangla-english": "bn",
}


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "tts_audio"


def extract_text(package: dict[str, Any]) -> str:
    """Extract the best available narration text from a voice package."""

    for field in TEXT_FIELDS:
        value = str(package.get(field, "")).strip()
        if value:
            return value
    return ""


def language_code(package: dict[str, Any]) -> str:
    language = str(package.get("language", "Bangla")).strip().lower()
    return LANGUAGE_CODE_BY_NAME.get(language, "bn")


def resolve_audio_output_path(package: dict[str, Any], package_path: Path) -> Path:
    existing = str(package.get("audio_output_path", package.get("suggested_audio_path", ""))).strip()
    if existing:
        path = Path(existing)
        if path.suffix.lower() != ".mp3":
            path = path.with_suffix(".mp3")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    AUDIO_OUTPUTS.mkdir(parents=True, exist_ok=True)
    project = safe_name(str(package.get("project_preset", "general")))
    title = safe_name(str(package.get("title", package_path.stem)))
    return AUDIO_OUTPUTS / f"generic_tts_{project}_{title}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"


def validate_generic_tts_rules(package: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    voice_mode = str(package.get("voice_mode", "")).strip().lower()
    if voice_mode in BLOCKED_VOICE_MODES:
        messages.append("Generic TTS adapter does not support reference voice clone mode.")
    if package.get("reference_voice_path"):
        messages.append("Generic TTS adapter does not use reference_voice_path. Use original/generic voice mode for this backend.")
    if not extract_text(package):
        messages.append("No narration text found. Add script_draft, voiceover_text, text, or combined_package.")
    return messages


def generate_gtts_audio(text: str, output_path: Path, lang: str) -> None:
    """Generate MP3 audio using gTTS.

    gTTS is imported lazily so the rest of Naz Lab remains lightweight.
    """

    try:
        from gtts import gTTS
    except ImportError as exc:
        raise RuntimeError("gTTS is not installed. Run: pip install -q gTTS") from exc

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(str(output_path))


def run_generic_tts(package_path: Path, allow_draft: bool = False) -> dict[str, Any]:
    package = safe_read_json(package_path, {})
    if not isinstance(package, dict):
        return {"ok": False, "status": "blocked", "messages": ["Voice package JSON must be an object."], "package_path": str(package_path)}

    backend_status = str(package.get("backend_status", package.get("status", "draft")))
    if backend_status != "ready_for_backend" and not allow_draft:
        return {
            "ok": False,
            "status": "blocked",
            "messages": ["Package backend_status must be ready_for_backend. Use --allow-draft only for manual testing."],
            "package_path": str(package_path),
        }

    validation = validate_backend_package(package, kind="voice", source_path=package_path)
    rule_messages = validate_generic_tts_rules(package)
    if not validation.ok or rule_messages:
        messages = list(validation.messages) + rule_messages
        try:
            mark_backend_failed(package_path, "; ".join(messages))
        except Exception:
            pass
        return {"ok": False, "status": "blocked", "messages": messages, "warnings": validation.warnings, "package_path": str(package_path)}

    text = extract_text(package)
    output_path = resolve_audio_output_path(package, package_path)
    lang = language_code(package)

    try:
        mark_backend_status(package_path, "running", "Generic gTTS backend started.", allow_any_transition=True)
        generate_gtts_audio(text, output_path, lang)
        package = safe_read_json(package_path, {})
        if isinstance(package, dict):
            package["audio_output_path"] = str(output_path)
            package["backend_adapter"] = "generic_tts_gtts_adapter"
            package["backend_status"] = "completed"
            package["backend_last_updated"] = datetime.now().isoformat(timespec="seconds")
            package.setdefault("backend_events", [])
            package["backend_events"].append({"timestamp": datetime.now().isoformat(timespec="seconds"), "level": "info", "message": "Generic gTTS audio generated."})
            safe_write_json(package_path, package)
        append_output_log(
            OUTPUT_LOG_JSON,
            workstation="generic_tts_backend",
            event="audio_generated",
            details={"package_path": str(package_path), "audio_output_path": str(output_path), "adapter": "generic_tts_gtts_adapter"},
        )
        return {"ok": True, "status": "completed", "audio_output_path": str(output_path), "package_path": str(package_path), "language_code": lang}
    except Exception as exc:
        try:
            mark_backend_failed(package_path, f"Generic gTTS backend failed: {exc}")
        except Exception:
            pass
        return {"ok": False, "status": "failed", "messages": [str(exc)], "package_path": str(package_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate generic TTS audio from a Naz Lab voice package using gTTS.")
    parser.add_argument("package_path", help="Path to a voice backend package/job JSON file.")
    parser.add_argument("--allow-draft", action="store_true", help="Allow draft package status for manual testing.")
    args = parser.parse_args()
    result = run_generic_tts(Path(args.package_path), allow_draft=args.allow_draft)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
