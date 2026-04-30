"""Text Builder persistence and job-queue helpers for Naz Lab.

This module centralizes fragile workflow pieces:
1. Structured metadata sidecar files for every saved/generated text output.
2. Automatic Image Job JSON export for Prompt Improver outputs.
3. Text-to-Voice job creation.
4. Package draft creation.

It is intentionally dependency-light so both the unified dashboard and legacy
Text Workstation can import it safely in Colab.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from shared.drive_paths import IMAGE_JOBS, OUTPUT_LOG_JSON, PACKAGE_DRAFTS, TEXT_METADATA, VOICE_JOBS
from shared.json_utils import append_output_log, safe_write_json

DEFAULT_NEGATIVE_PROMPT = "no fake logo, no watermark, no distorted face"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text)).strip("_")[:80] or "naz_lab"


def ensure_text_pipeline_dirs() -> None:
    TEXT_METADATA.mkdir(parents=True, exist_ok=True)
    IMAGE_JOBS.mkdir(parents=True, exist_ok=True)
    VOICE_JOBS.mkdir(parents=True, exist_ok=True)
    PACKAGE_DRAFTS.mkdir(parents=True, exist_ok=True)
    OUTPUT_LOG_JSON.parent.mkdir(parents=True, exist_ok=True)


def build_text_metadata(
    *,
    mode: str,
    project: str,
    language: str,
    topic: str,
    prompt: str,
    model: str,
    engine_status: str,
    output_text_path: str | Path | None,
    output_chars: int,
    source: str = "text_builder",
    metadata_version: str = "1.0",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "metadata_version": metadata_version,
        "source": source,
        "project": project,
        "mode": mode,
        "language": language,
        "topic": topic,
        "prompt": prompt,
        "model": model,
        "engine_status": engine_status,
        "created_at": now_iso(),
        "output_text_path": str(output_text_path or ""),
        "output_chars": output_chars,
        "extra": extra or {},
    }


def write_text_metadata(metadata: dict[str, Any]) -> Path:
    ensure_text_pipeline_dirs()
    path = TEXT_METADATA / f"text_metadata_{safe_slug(metadata.get('project', 'project'))}_{safe_slug(metadata.get('mode', 'mode'))}_{now_stamp()}_{uuid.uuid4().hex[:8]}.json"
    safe_write_json(path, metadata)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="text_workstation",
        event="text_metadata_saved",
        details={"path": str(path), "mode": metadata.get("mode", ""), "project": metadata.get("project", "")},
    )
    return path


def extract_positive_prompt(text: str) -> str:
    """Return a clean positive prompt from Prompt Improver output.

    If the output contains an explicit negative prompt section, only the content
    before that section is used as the positive prompt. This keeps negative
    prompts from being duplicated into image generation input.
    """
    markers = ["Negative prompt:", "Negative Prompt:", "negative prompt:", "NEGATIVE PROMPT:"]
    cleaned = text.strip()
    for marker in markers:
        if marker in cleaned:
            cleaned = cleaned.split(marker, 1)[0].strip()
            break
    return cleaned


def create_image_job_from_text(
    *,
    project: str,
    mode: str,
    topic: str,
    output_text: str,
    source_text_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    auto_export: bool = False,
) -> Path:
    """Create an Image Workstation-compatible queued JSON job."""
    ensure_text_pipeline_dirs()
    job_id = f"image_{uuid.uuid4().hex[:10]}"
    path = IMAGE_JOBS / f"image_job_{safe_slug(project)}_{safe_slug(mode)}_{now_stamp()}_{job_id}.json"
    positive_prompt = extract_positive_prompt(output_text) if mode == "Prompt Improver" else output_text.strip()
    data = {
        "job_id": job_id,
        "schema_version": "1.20",
        "source_workstation": "text_workstation",
        "target_workstation": "image_workstation",
        "source_mode": mode,
        "status": "queued",
        "review_status": "pending",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "project": project,
        "topic": topic,
        "auto_export": auto_export,
        "input_payload": {
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "format": "1:1 square by default; adapt to 9:16 for reels when requested",
        },
        "source_text_path": str(source_text_path or ""),
        "source_metadata_path": str(metadata_path or ""),
        "output_path": "",
        "errors": [],
    }
    safe_write_json(path, data)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="text_workstation",
        event="image_job_created",
        details={"path": str(path), "job_id": job_id, "auto_export": auto_export, "source_mode": mode},
    )
    return path


def create_voice_job(
    *,
    project: str,
    mode: str,
    language: str,
    topic: str,
    output_text: str,
    source_text_path: str | Path | None = None,
) -> Path:
    """Create a Voice Workstation-compatible queued JSON job from text output."""
    ensure_text_pipeline_dirs()
    job_id = f"voice_{uuid.uuid4().hex[:10]}"
    path = VOICE_JOBS / f"{job_id}.json"
    created = now_iso()
    record = {
        "job_id": job_id,
        "schema_version": "working-plan-v2.0",
        "source_workstation": "text_workstation",
        "target_workstation": "voice_workstation",
        "source_mode": mode,
        "project": project,
        "language": language,
        "topic": topic,
        "status": "queued",
        "review_status": "pending",
        "created_at": created,
        "updated_at": created,
        "source_text_path": str(source_text_path or ""),
        "input_payload": {"text": output_text, "voice_preset": "default", "requires_reference_audio_consent": True},
        "output_path": "",
        "errors": [],
        "history": [{"at": created, "event": "created", "by": "text_workstation"}],
    }
    safe_write_json(path, record)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="text_workstation",
        event="voice_job_created",
        details={"path": str(path), "job_id": job_id, "source_mode": mode},
    )
    return path


def create_package_draft(
    *,
    project: str,
    mode: str,
    language: str,
    topic: str,
    output_text: str,
    source_text_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
    image_job_path: str | Path | None = None,
    voice_job_path: str | Path | None = None,
) -> Path:
    """Create a package draft JSON from the current Text Workstation output."""
    ensure_text_pipeline_dirs()
    draft_id = f"package_{uuid.uuid4().hex[:10]}"
    path = PACKAGE_DRAFTS / f"{draft_id}.json"
    created = now_iso()
    record = {
        "package_id": draft_id,
        "schema_version": "working-plan-v2.0",
        "status": "draft",
        "review_status": "pending",
        "created_at": created,
        "updated_at": created,
        "project": project,
        "mode": mode,
        "language": language,
        "topic": topic,
        "content": output_text,
        "source_text_path": str(source_text_path or ""),
        "metadata_path": str(metadata_path or ""),
        "image_job_path": str(image_job_path or ""),
        "voice_job_path": str(voice_job_path or ""),
        "manual_gate": True,
        "facebook_posting_enabled": False,
        "video_generation_enabled": False,
        "notes": "Contextual package draft created from Text Workstation.",
    }
    safe_write_json(path, record)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="text_workstation",
        event="package_draft_created",
        details={"path": str(path), "package_id": draft_id, "source_mode": mode},
    )
    return path


def persist_text_result_and_optional_image_job(
    *,
    mode: str,
    project: str,
    language: str,
    topic: str,
    prompt: str,
    model: str,
    engine_status: str,
    output_text: str,
    output_text_path: str | Path | None,
    auto_image_job_for_prompt_improver: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Write metadata and optionally auto-export Prompt Improver output.

    Returns string paths so Streamlit session state can store them directly.
    """
    metadata = build_text_metadata(
        mode=mode,
        project=project,
        language=language,
        topic=topic,
        prompt=prompt,
        model=model,
        engine_status=engine_status,
        output_text_path=output_text_path,
        output_chars=len(output_text or ""),
        extra=extra,
    )
    metadata_path = write_text_metadata(metadata)
    image_job_path = ""
    if auto_image_job_for_prompt_improver and mode == "Prompt Improver" and output_text.strip():
        image_job_path = str(create_image_job_from_text(
            project=project,
            mode=mode,
            topic=topic,
            output_text=output_text,
            source_text_path=output_text_path,
            metadata_path=metadata_path,
            auto_export=True,
        ))
    return {"metadata_path": str(metadata_path), "image_job_path": image_job_path}
