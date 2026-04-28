"""Lightweight backend schema and status constants for Naz Lab.

This module contains no heavy model dependencies. It defines the shared contract
future backend adapters should follow before running image, voice, video, or
portrait generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BACKEND_PHASE = "Backend Adapter Skeletons 1.0"

BACKEND_STATUS = [
    "draft",
    "ready_for_backend",
    "running",
    "completed",
    "blocked",
    "failed",
    "archived",
]

BACKEND_KINDS = ["text", "image", "voice", "video", "portrait"]

REFERENCE_BACKEND_KINDS = {"voice", "portrait"}

STATUS_TRANSITIONS = {
    "draft": ["ready_for_backend", "archived"],
    "ready_for_backend": ["running", "blocked", "archived"],
    "running": ["completed", "failed", "blocked"],
    "completed": ["archived"],
    "blocked": ["ready_for_backend", "archived"],
    "failed": ["ready_for_backend", "archived"],
    "archived": [],
}

REQUIRED_FIELDS_BY_KIND = {
    "text": ["project_preset", "language"],
    "image": ["positive_prompt"],
    "voice": ["voice_mode", "tts_direction"],
    "video": ["project_preset"],
    "portrait": ["positive_prompt", "negative_prompt"],
}

OUTPUT_FIELD_BY_KIND = {
    "text": "text_output_path",
    "image": "image_output_path",
    "voice": "audio_output_path",
    "video": "video_output_path",
    "portrait": "portrait_output_path",
}


@dataclass
class BackendValidationResult:
    """Validation result returned by lightweight backend helpers."""

    ok: bool
    status: str = "ready_for_backend"
    messages: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "messages": self.messages,
            "warnings": self.warnings,
        }


def normalize_backend_kind(kind: str) -> str:
    """Normalize backend kind names used by adapters and queues."""

    normalized = kind.strip().lower().replace("_workstation", "")
    if normalized == "face":
        return "portrait"
    return normalized


def is_supported_backend_kind(kind: str) -> bool:
    """Return True when the backend kind is supported by the skeleton contract."""

    return normalize_backend_kind(kind) in BACKEND_KINDS


def infer_backend_kind_from_path(path: str | Path) -> str:
    """Infer backend kind from a package/job file path."""

    text = str(path).lower()
    if "voice" in text:
        return "voice"
    if "portrait" in text or "face" in text:
        return "portrait"
    if "video" in text:
        return "video"
    if "image" in text:
        return "image"
    if "text" in text or "script" in text or "chat" in text:
        return "text"
    return "text"


def default_backend_package(kind: str) -> dict[str, Any]:
    """Return a minimal package shell for a future backend adapter."""

    backend_kind = normalize_backend_kind(kind)
    return {
        "backend_phase": BACKEND_PHASE,
        "backend_kind": backend_kind,
        "backend_status": "draft",
        "backend_messages": [],
        "backend_warnings": [],
        "future_backend": "skeleton",
    }
