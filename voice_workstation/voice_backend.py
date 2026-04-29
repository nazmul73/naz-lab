"""Lightweight Voice Workstation backend for Naz Lab.

This module provides a safe Drive-backed voice workflow:
- create text-to-voice job JSON
- list voice jobs and outputs
- attach an existing audio output path to a job
- mark job status without requiring a heavy TTS engine

Real TTS generation can be connected later. This keeps the dashboard usable and
runtime-testable from the main Naz Lab app.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import VOICE_JOBS, VOICE_OUTPUTS, LOGS_DIR  # noqa: E402
from shared.job_queue_schema import read_json, write_json  # noqa: E402

VOICE_SCHEMA_VERSION = "1.0"
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
VALID_STATUSES = ["draft", "queued", "ready", "attached", "failed"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs() -> None:
    for folder in [VOICE_JOBS, VOICE_OUTPUTS, LOGS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def safe_slug(text: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text)).strip("_")
    return clean[:80] or "voice_job"


def make_voice_job_id() -> str:
    return f"voice_{uuid.uuid4().hex[:10]}"


def create_voice_job(*, project: str, topic: str, text: str, voice_preset: str = "Default", language: str = "Bangla", source_text_path: str = "") -> Path:
    ensure_dirs()
    job_id = make_voice_job_id()
    created = now_iso()
    record = {
        "job_id": job_id,
        "schema_version": VOICE_SCHEMA_VERSION,
        "source_workstation": "naz_lab",
        "target_workstation": "voice_workstation",
        "status": "queued",
        "review_status": "pending",
        "created_at": created,
        "updated_at": created,
        "project": project,
        "topic": topic,
        "language": language,
        "voice_preset": voice_preset,
        "input_text": text,
        "source_text_path": source_text_path,
        "output_audio_path": "",
        "metadata": {
            "engine": "pending_connection",
            "note": "Real TTS engine not connected yet. Attach existing audio or connect engine later.",
        },
        "errors": [],
    }
    path = VOICE_JOBS / f"voice_job_{safe_slug(project)}_{now_stamp()}_{job_id}.json"
    write_json(path, record)
    return path


def list_voice_jobs(limit: int = 200) -> list[Path]:
    ensure_dirs()
    files = sorted(VOICE_JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def list_voice_outputs(limit: int = 200) -> list[Path]:
    ensure_dirs()
    files = [p for p in VOICE_OUTPUTS.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def summarize_voice_job(path: Path) -> dict[str, Any]:
    data = read_json(path, {})
    if not isinstance(data, dict):
        data = {}
    return {
        "Job ID": data.get("job_id", path.stem),
        "Project": data.get("project", ""),
        "Topic": str(data.get("topic", ""))[:90],
        "Language": data.get("language", ""),
        "Voice": data.get("voice_preset", ""),
        "Status": data.get("status", ""),
        "Audio": data.get("output_audio_path", ""),
        "Path": str(path),
        "Modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }


def attach_audio_to_voice_job(job_path: str | Path, audio_path: str | Path) -> dict[str, Any]:
    ensure_dirs()
    job = Path(str(job_path))
    audio = Path(str(audio_path))
    if not job.exists():
        return {"ok": False, "reason": "voice job not found", "job_path": str(job)}
    if not audio.exists() or audio.suffix.lower() not in AUDIO_EXTENSIONS:
        return {"ok": False, "reason": "audio path not found or unsupported", "audio_path": str(audio)}
    data = read_json(job, {})
    if not isinstance(data, dict):
        return {"ok": False, "reason": "invalid voice job json", "job_path": str(job)}
    data["output_audio_path"] = str(audio)
    data["status"] = "attached"
    data["updated_at"] = now_iso()
    history = data.get("history", [])
    if not isinstance(history, list):
        history = []
    history.append({"at": now_iso(), "event": "audio_attached", "audio_path": str(audio)})
    data["history"] = history
    write_json(job, data)
    return {"ok": True, "job_path": str(job), "audio_path": str(audio), "status": "attached"}


def voice_runtime_status() -> dict[str, Any]:
    ensure_dirs()
    return {
        "voice_jobs_dir": str(VOICE_JOBS),
        "voice_outputs_dir": str(VOICE_OUTPUTS),
        "voice_jobs": len(list_voice_jobs()),
        "voice_outputs": len(list_voice_outputs()),
        "tts_engine_connected": False,
        "engine_status": "pending_connection",
        "note": "Drive-backed job/output workflow is ready. Real TTS engine can be connected later.",
    }


if __name__ == "__main__":
    print(json.dumps(voice_runtime_status(), ensure_ascii=False, indent=2))
