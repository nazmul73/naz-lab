"""Image placeholder backend adapter for Naz Lab.

This adapter creates a simple PNG placeholder from a validated image package/job.
It does not run Fooocus, Stable Diffusion, SDXL, ComfyUI, or any heavy image model.
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
from shared.drive_paths import IMAGE_OUTPUTS, OUTPUT_LOG_JSON  # noqa: E402
from shared.json_utils import append_output_log, safe_read_json, safe_write_json  # noqa: E402

PROMPT_FIELDS = ["positive_prompt", "prompt", "combined_prompt"]


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "image_output"


def extract_prompt(package: dict[str, Any]) -> str:
    for field in PROMPT_FIELDS:
        value = str(package.get(field, "")).strip()
        if value:
            return value
    return ""


def resolve_image_output_path(package: dict[str, Any], package_path: Path) -> Path:
    existing = str(package.get("image_output_path", package.get("suggested_output_path", ""))).strip()
    if existing:
        path = Path(existing)
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            path = path.with_suffix(".png")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    IMAGE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    project = safe_name(str(package.get("project_preset", "general")))
    title = safe_name(str(package.get("title", package_path.stem)))
    return IMAGE_OUTPUTS / f"placeholder_image_{project}_{title}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"


def validate_image_placeholder_rules(package: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    if not extract_prompt(package):
        messages.append("No image prompt found. Add positive_prompt, prompt, or combined_prompt.")
    return messages


def create_placeholder_png(package: dict[str, Any], output_path: Path) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("Pillow is not installed. Run: pip install -q pillow") from exc

    width, height = 1080, 1080
    image = Image.new("RGB", (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(image)

    project = str(package.get("project_preset", "General"))
    title = str(package.get("title", "Naz Lab Image Placeholder"))
    prompt = extract_prompt(package)[:450]
    negative = str(package.get("negative_prompt", ""))[:240]
    lines = [
        "Naz Lab Image Placeholder",
        f"Project: {project}",
        f"Title: {title}",
        "",
        "Prompt:",
    ]
    lines.extend([prompt[i : i + 80] for i in range(0, len(prompt), 80)])
    if negative:
        lines.extend(["", "Negative:"])
        lines.extend([negative[i : i + 80] for i in range(0, len(negative), 80)])
    lines.extend(["", "This is not final AI artwork.", "Backend: image_placeholder_adapter"])

    y = 60
    for line in lines:
        draw.text((60, y), line, fill=(20, 20, 20))
        y += 34
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def run_image_placeholder(package_path: Path, allow_draft: bool = False) -> dict[str, Any]:
    package = safe_read_json(package_path, {})
    if not isinstance(package, dict):
        return {"ok": False, "status": "blocked", "messages": ["Image package JSON must be an object."], "package_path": str(package_path)}

    backend_status = str(package.get("backend_status", package.get("status", "draft")))
    if backend_status != "ready_for_backend" and not allow_draft:
        return {
            "ok": False,
            "status": "blocked",
            "messages": ["Package backend_status must be ready_for_backend. Use --allow-draft only for manual testing."],
            "package_path": str(package_path),
        }

    validation = validate_backend_package(package, kind="image", source_path=package_path)
    rule_messages = validate_image_placeholder_rules(package)
    if not validation.ok or rule_messages:
        messages = list(validation.messages) + rule_messages
        try:
            mark_backend_failed(package_path, "; ".join(messages))
        except Exception:
            pass
        return {"ok": False, "status": "blocked", "messages": messages, "warnings": validation.warnings, "package_path": str(package_path)}

    output_path = resolve_image_output_path(package, package_path)
    try:
        mark_backend_status(package_path, "running", "Image placeholder backend started.", allow_any_transition=True)
        create_placeholder_png(package, output_path)
        package = safe_read_json(package_path, {})
        if isinstance(package, dict):
            package["image_output_path"] = str(output_path)
            package["backend_adapter"] = "image_placeholder_adapter"
            package["backend_status"] = "completed"
            package["backend_last_updated"] = datetime.now().isoformat(timespec="seconds")
            package.setdefault("backend_events", [])
            package["backend_events"].append({"timestamp": datetime.now().isoformat(timespec="seconds"), "level": "info", "message": "Image placeholder PNG generated."})
            safe_write_json(package_path, package)
        append_output_log(
            OUTPUT_LOG_JSON,
            workstation="image_placeholder_backend",
            event="image_placeholder_generated",
            details={"package_path": str(package_path), "image_output_path": str(output_path), "adapter": "image_placeholder_adapter"},
        )
        return {"ok": True, "status": "completed", "image_output_path": str(output_path), "package_path": str(package_path)}
    except Exception as exc:
        try:
            mark_backend_failed(package_path, f"Image placeholder backend failed: {exc}")
        except Exception:
            pass
        return {"ok": False, "status": "failed", "messages": [str(exc)], "package_path": str(package_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a placeholder PNG from a Naz Lab image package/job.")
    parser.add_argument("package_path", help="Path to an image backend package/job JSON file.")
    parser.add_argument("--allow-draft", action="store_true", help="Allow draft package status for manual testing.")
    args = parser.parse_args()
    result = run_image_placeholder(Path(args.package_path), allow_draft=args.allow_draft)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
