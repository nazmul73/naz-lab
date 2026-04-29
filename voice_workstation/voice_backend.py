"""Lightweight Voice Workstation backend for Naz Lab.

Provides a safe Drive-backed voice workflow:
- create text-to-voice job JSON
- list voice jobs and outputs
- attach an existing audio output path to a job
- inspect/configure a pluggable TTS engine without requiring one by default

Real TTS generation is intentionally pluggable. If no final engine is selected,
the dashboard remains stable and runtime-testable.
"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import CONFIG_DIR, LOGS_DIR, VOICE_JOBS, VOICE_OUTPUTS  # noqa: E402
from shared.job_queue_schema import read_json, write_json  # noqa: E402

VOICE_SCHEMA_VERSION = "1.0"
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
VALID_STATUSES = ["draft", "queued", "ready", "attached", "failed"]
VOICE_CONFIG_JSON = CONFIG_DIR / "voice_engine_config.json"
VOICE_LOG_JSON = LOGS_DIR / "voice_workstation_log.json"
DEFAULT_VOICE_CONFIG = {
    "engine_enabled": False,
    "engine_name": "pending_selection",
    "engine_command": "",
    "output_extension": ".wav",
    "notes": "Set engine_enabled=true only after selecting and testing a real TTS engine. Until then, voice jobs and audio attachment remain available.",
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs() -> None:
    for folder in [VOICE_JOBS, VOICE_OUTPUTS, LOGS_DIR, CONFIG_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
    if not VOICE_CONFIG_JSON.exists():
        write_json(VOICE_CONFIG_JSON, DEFAULT_VOICE_CONFIG)
    if not VOICE_LOG_JSON.exists():
        write_json(VOICE_LOG_JSON, {"items": []})


def log_event(event: dict[str, Any]) -> None:
    ensure_dirs()
    data = read_json(VOICE_LOG_JSON, {"items": []})
    items = data.get("items", []) if isinstance(data, dict) else []
    if not isinstance(items, list):
        items = []
    items.insert(0, {"at": now_iso(), **event})
    write_json(VOICE_LOG_JSON, {"updated_at": now_iso(), "items": items[:500]})


def safe_slug(text: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text)).strip("_")
    return clean[:80] or "voice_job"


def make_voice_job_id() -> str:
    return f"voice_{uuid.uuid4().hex[:10]}"


def get_voice_config() -> dict[str, Any]:
    ensure_dirs()
    data = read_json(VOICE_CONFIG_JSON, DEFAULT_VOICE_CONFIG)
    if not isinstance(data, dict):
        data = DEFAULT_VOICE_CONFIG.copy()
        write_json(VOICE_CONFIG_JSON, data)
    return {**DEFAULT_VOICE_CONFIG, **data}


def save_voice_config(config: dict[str, Any]) -> dict[str, Any]:
    ensure_dirs()
    merged = {**DEFAULT_VOICE_CONFIG, **config}
    write_json(VOICE_CONFIG_JSON, merged)
    log_event({"event": "voice_config_saved", "engine_name": merged.get("engine_name"), "engine_enabled": merged.get("engine_enabled")})
    return merged


def engine_available(config: dict[str, Any] | None = None) -> bool:
    config = config or get_voice_config()
    if not config.get("engine_enabled"):
        return False
    command = str(config.get("engine_command", "")).strip()
    if not command:
        return False
    executable = command.split()[0]
    return bool(shutil.which(executable) or Path(executable).exists())


def create_voice_job(*, project: str, topic: str, text: str, voice_preset: str = "Default", language: str = "Bangla", source_text_path: str = "") -> Path:
    ensure_dirs()
    job_id = make_voice_job_id()
    created = now_iso()
    config = get_voice_config()
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
            "engine": config.get("engine_name", "pending_selection"),
            "engine_enabled": bool(config.get("engine_enabled")),
            "engine_available": engine_available(config),
            "note": "Real TTS engine is pluggable. Attach existing audio or connect a tested engine.",
        },
        "errors": [],
    }
    path = VOICE_JOBS / f"voice_job_{safe_slug(project)}_{now_stamp()}_{job_id}.json"
    write_json(path, record)
    log_event({"event": "voice_job_created", "job_id": job_id, "path": str(path)})
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
    log_event({"event": "audio_attached", "job_path": str(job), "audio_path": str(audio)})
    return {"ok": True, "job_path": str(job), "audio_path": str(audio), "status": "attached"}


def voice_runtime_status() -> dict[str, Any]:
    ensure_dirs()
    config = get_voice_config()
    return {
        "voice_jobs_dir": str(VOICE_JOBS),
        "voice_outputs_dir": str(VOICE_OUTPUTS),
        "voice_config_path": str(VOICE_CONFIG_JSON),
        "voice_log_path": str(VOICE_LOG_JSON),
        "voice_jobs": len(list_voice_jobs()),
        "voice_outputs": len(list_voice_outputs()),
        "tts_engine_connected": engine_available(config),
        "engine_enabled": bool(config.get("engine_enabled")),
        "engine_name": config.get("engine_name"),
        "engine_status": "available" if engine_available(config) else "pending_connection",
        "note": "Drive-backed job/output workflow is ready. Real TTS engine can be connected by config.",
    }


if __name__ == "__main__":
    print(json.dumps(voice_runtime_status(), ensure_ascii=False, indent=2))
