"""Naz Lab Real Image Backend Phase 3.1.

This module turns queued image_job JSON files into real image files using a
Diffusers Stable Diffusion pipeline on Colab GPU when available.

Design goals:
- Read Phase 1.10 image job JSON records.
- Validate shared job schema.
- Update job status: queued -> processing -> done/failed.
- Save generated PNG files to Google Drive image_outputs.
- Save metadata JSON beside each generated image.
- Fall back to placeholder metadata if diffusers/torch/model is unavailable.

Default model:
- runwayml/stable-diffusion-v1-5

The backend is intentionally API-light and Colab-friendly. It does not run on
import. Use process_pending_real_image_jobs() or run this file directly.
"""

from __future__ import annotations

import json
import os
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import COMPLETED_JOBS, IMAGE_JOBS, IMAGE_OUTPUTS, LOGS_DIR  # noqa: E402
from shared.job_queue_schema import read_json, validate_job_record, write_json  # noqa: E402

BACKEND_VERSION = "real-image-backend-phase-3.1"
DEFAULT_MODEL_ID = os.environ.get("NAZ_LAB_IMAGE_MODEL", "runwayml/stable-diffusion-v1-5")
DEFAULT_NEGATIVE_PROMPT = "no fake logo, no watermark, no distorted face"
DEFAULT_WIDTH = int(os.environ.get("NAZ_LAB_IMAGE_WIDTH", "512"))
DEFAULT_HEIGHT = int(os.environ.get("NAZ_LAB_IMAGE_HEIGHT", "512"))
DEFAULT_STEPS = int(os.environ.get("NAZ_LAB_IMAGE_STEPS", "20"))
DEFAULT_GUIDANCE = float(os.environ.get("NAZ_LAB_IMAGE_GUIDANCE", "7.0"))

_PIPELINE_CACHE: dict[str, Any] = {}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_dirs() -> None:
    for folder in [IMAGE_JOBS, IMAGE_OUTPUTS, COMPLETED_JOBS, LOGS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def append_history(job: dict[str, Any], event: str, message: str = "") -> None:
    history = job.setdefault("history", [])
    if isinstance(history, list):
        history.append({"at": now_iso(), "event": event, "by": BACKEND_VERSION, "message": message})


def set_status(job: dict[str, Any], status: str, message: str = "") -> None:
    job["status"] = status
    job["updated_at"] = now_iso()
    append_history(job, status, message)


def get_prompt_payload(job: dict[str, Any]) -> tuple[str, str]:
    payload = job.get("input_payload", {}) if isinstance(job.get("input_payload"), dict) else {}
    positive = str(payload.get("positive_prompt", job.get("prompt", ""))).strip()
    negative = str(payload.get("negative_prompt", DEFAULT_NEGATIVE_PROMPT)).strip() or DEFAULT_NEGATIVE_PROMPT
    return positive, negative


def runtime_status() -> dict[str, Any]:
    status: dict[str, Any] = {
        "backend_version": BACKEND_VERSION,
        "generated_at": now_iso(),
        "model_id": DEFAULT_MODEL_ID,
        "image_outputs": str(IMAGE_OUTPUTS),
    }
    try:
        import torch  # type: ignore

        status["torch_available"] = True
        status["cuda_available"] = bool(torch.cuda.is_available())
        status["device"] = "cuda" if torch.cuda.is_available() else "cpu"
        status["torch_version"] = str(torch.__version__)
    except Exception as exc:
        status["torch_available"] = False
        status["cuda_available"] = False
        status["device"] = "unavailable"
        status["torch_error"] = str(exc)
    try:
        import diffusers  # type: ignore

        status["diffusers_available"] = True
        status["diffusers_version"] = str(diffusers.__version__)
    except Exception as exc:
        status["diffusers_available"] = False
        status["diffusers_error"] = str(exc)
    write_json(LOGS_DIR / "real_image_backend_status.json", status)
    return status


def load_pipeline(model_id: str = DEFAULT_MODEL_ID) -> Any:
    if model_id in _PIPELINE_CACHE:
        return _PIPELINE_CACHE[model_id]
    import torch  # type: ignore
    from diffusers import StableDiffusionPipeline  # type: ignore

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype, safety_checker=None)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)
    if hasattr(pipe, "enable_attention_slicing"):
        pipe.enable_attention_slicing()
    _PIPELINE_CACHE[model_id] = pipe
    return pipe


def save_metadata(path: Path, metadata: dict[str, Any]) -> Path:
    metadata_path = path.with_suffix(".metadata.json")
    write_json(metadata_path, metadata)
    return metadata_path


def generate_real_image(job: dict[str, Any], job_path: Path, *, model_id: str = DEFAULT_MODEL_ID) -> dict[str, Any]:
    positive, negative = get_prompt_payload(job)
    if not positive:
        raise ValueError("positive prompt is empty")

    job_id = str(job.get("job_id", job_path.stem))
    output_path = IMAGE_OUTPUTS / f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    status = runtime_status()
    if not status.get("torch_available") or not status.get("diffusers_available"):
        raise RuntimeError("torch/diffusers unavailable; install Phase 3.1 dependencies first")
    if not status.get("cuda_available"):
        raise RuntimeError("CUDA GPU unavailable; connect Colab GPU for real image generation")

    pipe = load_pipeline(model_id)
    result = pipe(
        prompt=positive,
        negative_prompt=negative,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        num_inference_steps=DEFAULT_STEPS,
        guidance_scale=DEFAULT_GUIDANCE,
    )
    image = result.images[0]
    IMAGE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

    metadata = {
        "backend_version": BACKEND_VERSION,
        "created_at": now_iso(),
        "job_id": job_id,
        "job_path": str(job_path),
        "model_id": model_id,
        "positive_prompt": positive,
        "negative_prompt": negative,
        "width": DEFAULT_WIDTH,
        "height": DEFAULT_HEIGHT,
        "num_inference_steps": DEFAULT_STEPS,
        "guidance_scale": DEFAULT_GUIDANCE,
        "output_path": str(output_path),
        "status": "done",
    }
    metadata_path = save_metadata(output_path, metadata)
    return {"output_path": str(output_path), "metadata_path": str(metadata_path), "metadata": metadata}


def process_real_image_job(job_path: Path, *, move_completed: bool = False, model_id: str = DEFAULT_MODEL_ID) -> dict[str, Any]:
    ensure_dirs()
    job = read_json(job_path, {})
    if not isinstance(job, dict):
        return {"path": str(job_path), "ok": False, "status": "failed", "message": "job file is not valid JSON object"}

    ok, messages = validate_job_record(job)
    if not ok:
        job.setdefault("errors", [])
        if isinstance(job["errors"], list):
            job["errors"].extend(messages)
        set_status(job, "failed", "schema validation failed")
        write_json(job_path, job)
        return {"path": str(job_path), "ok": False, "status": "failed", "message": "; ".join(messages)}

    status = str(job.get("status", "queued"))
    if status not in ["created", "queued", "failed"]:
        return {"path": str(job_path), "ok": True, "status": status, "message": "skipped non-queued job"}

    try:
        set_status(job, "processing", "real image backend picked up job")
        write_json(job_path, job)
        output = generate_real_image(job, job_path, model_id=model_id)
        job["output_path"] = output["output_path"]
        job["output_metadata_path"] = output["metadata_path"]
        set_status(job, "done", "real image generated")
        write_json(job_path, job)
        completed_copy = ""
        if move_completed:
            completed_path = COMPLETED_JOBS / job_path.name
            shutil.copy2(job_path, completed_path)
            completed_copy = str(completed_path)
        return {"path": str(job_path), "ok": True, "status": "done", "output_path": output["output_path"], "metadata_path": output["metadata_path"], "completed_copy": completed_copy}
    except Exception as exc:
        job.setdefault("errors", [])
        if isinstance(job["errors"], list):
            job["errors"].append(str(exc))
            job["errors"].append(traceback.format_exc()[-3000:])
        set_status(job, "failed", str(exc))
        write_json(job_path, job)
        return {"path": str(job_path), "ok": False, "status": "failed", "message": str(exc)}


def process_pending_real_image_jobs(limit: int = 5, *, move_completed: bool = False, model_id: str = DEFAULT_MODEL_ID) -> dict[str, Any]:
    ensure_dirs()
    job_files = sorted(IMAGE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime)[:limit]
    results = [process_real_image_job(path, move_completed=move_completed, model_id=model_id) for path in job_files]
    report = {"backend_version": BACKEND_VERSION, "created_at": now_iso(), "model_id": model_id, "processed": results}
    write_json(LOGS_DIR / "real_image_backend_last_run.json", report)
    return report


if __name__ == "__main__":
    print(json.dumps(process_pending_real_image_jobs(), ensure_ascii=False, indent=2))
