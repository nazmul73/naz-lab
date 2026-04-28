"""Naz Lab Final Content Package backend.

Phase target: Final Content Package Flow items 1-10.

This module builds portable package JSON records that bind together:
- saved text output
- image job JSON
- generated image output
- image metadata
- manual prompt and optional reference image paths
- package approval/export state

It is intentionally light and safe to run without GPU. Real image generation is
handled by image_workstation.real_image_backend_phase31 when GPU is available.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, IMAGE_JOBS, IMAGE_OUTPUTS, LOGS_DIR, TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS  # noqa: E402
from shared.job_queue_schema import read_json, write_json, summarize_job_file  # noqa: E402

PACKAGE_SCHEMA_VERSION = "1.0"
PACKAGE_DIR = BASE_PATH / "final_packages"
APPROVED_PACKAGE_DIR = PACKAGE_DIR / "approved"
EXPORTED_PACKAGE_DIR = PACKAGE_DIR / "exports"
REFERENCE_IMAGE_DIR = BASE_PATH / "reference_images"
PACKAGE_INDEX_JSON = PACKAGE_DIR / "package_index.json"
APPROVED_PACKAGES_JSON = PACKAGE_DIR / "approved_packages.json"
VALID_SOURCE_MODES = ["auto_job", "manual_prompt", "manual_prompt_with_reference"]
VALID_PACKAGE_STATUSES = ["draft", "ready", "approved", "rejected", "exported"]
DEFAULT_NEGATIVE_PROMPT = "no fake logo, no watermark, no distorted face"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs() -> None:
    for folder in [PACKAGE_DIR, APPROVED_PACKAGE_DIR, EXPORTED_PACKAGE_DIR, REFERENCE_IMAGE_DIR, IMAGE_OUTPUTS, LOGS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
    if not PACKAGE_INDEX_JSON.exists():
        write_json(PACKAGE_INDEX_JSON, {"items": []})
    if not APPROVED_PACKAGES_JSON.exists():
        write_json(APPROVED_PACKAGES_JSON, {"items": []})


def safe_slug(text: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")
    return clean[:90] or "naz_lab_package"


def make_package_id() -> str:
    return f"pkg_{uuid.uuid4().hex[:12]}"


def latest_text_outputs(limit: int = 200) -> list[Path]:
    files: list[Path] = []
    for folder in [TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS]:
        if folder.exists():
            files.extend(folder.glob("*.txt"))
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def latest_image_jobs(limit: int = 200) -> list[Path]:
    if not IMAGE_JOBS.exists():
        return []
    return sorted(IMAGE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def latest_image_outputs(limit: int = 200) -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    files = [p for p in IMAGE_OUTPUTS.rglob("*") if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def metadata_for_image(image_path: str | Path | None) -> str:
    if not image_path:
        return ""
    path = Path(str(image_path))
    metadata = path.with_suffix(".metadata.json")
    return str(metadata) if metadata.exists() else ""


def copy_reference_images(reference_paths: list[str] | None) -> list[str]:
    ensure_dirs()
    copied: list[str] = []
    for item in reference_paths or []:
        src = Path(str(item))
        if not src.exists() or not src.is_file():
            continue
        dest = REFERENCE_IMAGE_DIR / f"ref_{now_stamp()}_{uuid.uuid4().hex[:6]}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        copied.append(str(dest))
    return copied


def package_record(
    *,
    project: str,
    topic: str,
    source_mode: str,
    text_output_path: str = "",
    image_job_path: str = "",
    generated_image_path: str = "",
    image_metadata_path: str = "",
    manual_prompt: str = "",
    reference_images: list[str] | None = None,
    caption_text: str = "",
    notes: str = "",
    status: str = "draft",
    review_status: str = "pending",
) -> dict[str, Any]:
    if source_mode not in VALID_SOURCE_MODES:
        raise ValueError(f"source_mode must be one of {VALID_SOURCE_MODES}")
    if status not in VALID_PACKAGE_STATUSES:
        raise ValueError(f"status must be one of {VALID_PACKAGE_STATUSES}")
    package_id = make_package_id()
    created = now_iso()
    if generated_image_path and not image_metadata_path:
        image_metadata_path = metadata_for_image(generated_image_path)
    return {
        "package_id": package_id,
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "created_at": created,
        "updated_at": created,
        "project": project,
        "topic": topic,
        "status": status,
        "review_status": review_status,
        "source_mode": source_mode,
        "text_output_path": text_output_path,
        "image_job_path": image_job_path,
        "generated_image_path": generated_image_path,
        "image_metadata_path": image_metadata_path,
        "manual_prompt": manual_prompt,
        "reference_images": reference_images or [],
        "caption_text": caption_text,
        "notes": notes,
        "package_assets": {
            "text_output_path": text_output_path,
            "image_job_path": image_job_path,
            "generated_image_path": generated_image_path,
            "image_metadata_path": image_metadata_path,
            "reference_images": reference_images or [],
        },
        "history": [{"at": created, "event": "created", "by": "final_package_backend"}],
    }


def save_package(record: dict[str, Any]) -> Path:
    ensure_dirs()
    record["updated_at"] = now_iso()
    package_id = record.get("package_id") or make_package_id()
    record["package_id"] = package_id
    path = PACKAGE_DIR / f"{package_id}_{safe_slug(str(record.get('project', 'project')))}_{now_stamp()}.json"
    write_json(path, record)
    update_package_index(path, record)
    return path


def update_package_index(package_path: Path, record: dict[str, Any]) -> None:
    ensure_dirs()
    data = read_json(PACKAGE_INDEX_JSON, {"items": []})
    items = data.get("items", []) if isinstance(data, dict) else []
    items = [item for item in items if item.get("package_id") != record.get("package_id")]
    items.insert(0, {
        "package_id": record.get("package_id", ""),
        "project": record.get("project", ""),
        "topic": record.get("topic", ""),
        "status": record.get("status", ""),
        "review_status": record.get("review_status", ""),
        "source_mode": record.get("source_mode", ""),
        "generated_image_path": record.get("generated_image_path", ""),
        "package_path": str(package_path),
        "updated_at": record.get("updated_at", now_iso()),
    })
    write_json(PACKAGE_INDEX_JSON, {"updated_at": now_iso(), "items": items[:500]})


def build_auto_package(*, project: str, topic: str, text_output_path: str = "", image_job_path: str = "") -> Path:
    job = read_json(Path(image_job_path), {}) if image_job_path else {}
    image_path = str(job.get("output_path", "")) if isinstance(job, dict) else ""
    metadata_path = str(job.get("output_metadata_path", "")) if isinstance(job, dict) else metadata_for_image(image_path)
    payload = job.get("input_payload", {}) if isinstance(job, dict) and isinstance(job.get("input_payload"), dict) else {}
    prompt = str(payload.get("positive_prompt", ""))
    record = package_record(
        project=project,
        topic=topic,
        source_mode="auto_job",
        text_output_path=text_output_path,
        image_job_path=image_job_path,
        generated_image_path=image_path,
        image_metadata_path=metadata_path,
        manual_prompt=prompt,
        status="ready" if image_path else "draft",
        notes="Auto package built from saved text output and image job JSON.",
    )
    return save_package(record)


def build_manual_prompt_package(*, project: str, topic: str, manual_prompt: str, generated_image_path: str = "", caption_text: str = "") -> Path:
    record = package_record(
        project=project,
        topic=topic,
        source_mode="manual_prompt",
        manual_prompt=manual_prompt,
        generated_image_path=generated_image_path,
        image_metadata_path=metadata_for_image(generated_image_path),
        caption_text=caption_text,
        status="ready" if generated_image_path else "draft",
        notes="Manual prompt package. Image can be generated later or attached now.",
    )
    return save_package(record)


def build_reference_package(*, project: str, topic: str, manual_prompt: str, reference_paths: list[str], generated_image_path: str = "", caption_text: str = "") -> Path:
    copied_refs = copy_reference_images(reference_paths)
    record = package_record(
        project=project,
        topic=topic,
        source_mode="manual_prompt_with_reference",
        manual_prompt=manual_prompt,
        reference_images=copied_refs,
        generated_image_path=generated_image_path,
        image_metadata_path=metadata_for_image(generated_image_path),
        caption_text=caption_text,
        status="ready" if generated_image_path else "draft",
        notes="Manual prompt package with reference image support.",
    )
    return save_package(record)


def approve_package(package_path: str | Path, note: str = "") -> dict[str, Any]:
    ensure_dirs()
    path = Path(str(package_path))
    record = read_json(path, {})
    if not isinstance(record, dict):
        raise ValueError(f"invalid package JSON: {path}")
    record["status"] = "approved"
    record["review_status"] = "approved"
    record["updated_at"] = now_iso()
    record.setdefault("history", [])
    if isinstance(record["history"], list):
        record["history"].append({"at": now_iso(), "event": "approved", "by": "final_package_backend", "message": note})
    write_json(path, record)
    approved_path = APPROVED_PACKAGE_DIR / path.name
    write_json(approved_path, record)
    data = read_json(APPROVED_PACKAGES_JSON, {"items": []})
    items = data.get("items", []) if isinstance(data, dict) else []
    items = [item for item in items if item.get("package_id") != record.get("package_id")]
    items.insert(0, {"package_id": record.get("package_id"), "package_path": str(path), "approved_copy": str(approved_path), "project": record.get("project", ""), "topic": record.get("topic", ""), "updated_at": now_iso()})
    write_json(APPROVED_PACKAGES_JSON, {"updated_at": now_iso(), "items": items[:500]})
    update_package_index(path, record)
    return {"ok": True, "package_path": str(path), "approved_copy": str(approved_path), "package_id": record.get("package_id")}


def export_package(package_path: str | Path) -> dict[str, Any]:
    ensure_dirs()
    src = Path(str(package_path))
    record = read_json(src, {})
    if not isinstance(record, dict):
        raise ValueError(f"invalid package JSON: {src}")
    export_dir = EXPORTED_PACKAGE_DIR / str(record.get("package_id", src.stem))
    export_dir.mkdir(parents=True, exist_ok=True)
    exported_assets: list[str] = []
    for key in ["text_output_path", "image_job_path", "generated_image_path", "image_metadata_path"]:
        value = str(record.get(key, ""))
        if value and Path(value).exists():
            dest = export_dir / Path(value).name
            shutil.copy2(value, dest)
            exported_assets.append(str(dest))
    for ref in record.get("reference_images", []) if isinstance(record.get("reference_images", []), list) else []:
        if ref and Path(ref).exists():
            dest = export_dir / Path(ref).name
            shutil.copy2(ref, dest)
            exported_assets.append(str(dest))
    record["status"] = "exported"
    record["exported_at"] = now_iso()
    record["export_dir"] = str(export_dir)
    record["exported_assets"] = exported_assets
    write_json(export_dir / "package.json", record)
    write_json(src, record)
    update_package_index(src, record)
    return {"ok": True, "export_dir": str(export_dir), "exported_assets": exported_assets, "package_json": str(export_dir / "package.json")}


def list_packages(limit: int = 300) -> list[dict[str, Any]]:
    ensure_dirs()
    files = sorted(PACKAGE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    rows: list[dict[str, Any]] = []
    for path in files:
        if path.name in [PACKAGE_INDEX_JSON.name, APPROVED_PACKAGES_JSON.name]:
            continue
        record = read_json(path, {})
        if isinstance(record, dict):
            rows.append({
                "Package": record.get("package_id", path.stem),
                "Project": record.get("project", ""),
                "Topic": str(record.get("topic", ""))[:120],
                "Status": record.get("status", ""),
                "Review": record.get("review_status", ""),
                "Mode": record.get("source_mode", ""),
                "Image": record.get("generated_image_path", ""),
                "Path": str(path),
                "Modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
    return rows


def package_preview(package_path: str | Path) -> dict[str, Any]:
    path = Path(str(package_path))
    record = read_json(path, {})
    if not isinstance(record, dict):
        return {"ok": False, "message": "invalid package JSON", "path": str(path)}
    text_preview = ""
    text_path = str(record.get("text_output_path", ""))
    if text_path and Path(text_path).exists():
        text_preview = Path(text_path).read_text(encoding="utf-8", errors="ignore")[:2500]
    return {
        "ok": True,
        "package_path": str(path),
        "record": record,
        "text_preview": text_preview,
        "image_exists": bool(record.get("generated_image_path") and Path(str(record.get("generated_image_path"))).exists()),
        "metadata_exists": bool(record.get("image_metadata_path") and Path(str(record.get("image_metadata_path"))).exists()),
    }


if __name__ == "__main__":
    print(json.dumps({"package_dir": str(PACKAGE_DIR), "packages": list_packages()}, ensure_ascii=False, indent=2))
