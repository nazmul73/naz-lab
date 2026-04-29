"""Ollama model persistence helpers for Naz Lab Colab runtimes.

The goal is to keep downloaded Ollama models on Google Drive and expose them
through the default local Ollama model path after a Colab restart. The helper is
safe to call repeatedly from Streamlit panels or launchers.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from shared.drive_paths import OLLAMA_MODELS

DEFAULT_LOCAL_OLLAMA_MODELS = Path.home() / ".ollama" / "models"


def _has_files(path: Path) -> bool:
    try:
        return path.exists() and any(path.iterdir())
    except Exception:
        return False


def _copy_contents(src: Path, dst: Path) -> int:
    copied = 0
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if target.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
        copied += 1
    return copied


def ensure_ollama_persistence(
    drive_models_dir: Path = OLLAMA_MODELS,
    local_models_dir: Path | None = None,
) -> dict[str, Any]:
    """Ensure Ollama models persist through Drive-backed storage.

    Returns a status dictionary that can be displayed in Health/Text panels.
    It never raises for normal filesystem conflicts; failures are reported in
    the returned status so the UI can remain stable.
    """

    local_dir = local_models_dir or Path(os.environ.get("OLLAMA_MODELS", DEFAULT_LOCAL_OLLAMA_MODELS))
    drive_dir = drive_models_dir
    status: dict[str, Any] = {
        "ok": False,
        "mode": "unknown",
        "drive_models_dir": str(drive_dir),
        "local_models_dir": str(local_dir),
        "env_OLLAMA_MODELS": str(drive_dir),
        "copied_items": 0,
        "message": "",
    }

    try:
        os.environ["OLLAMA_MODELS"] = str(drive_dir)
        drive_dir.mkdir(parents=True, exist_ok=True)
        local_dir.parent.mkdir(parents=True, exist_ok=True)

        if local_dir.is_symlink():
            target = local_dir.resolve()
            status.update({
                "ok": target == drive_dir.resolve(),
                "mode": "already_symlinked",
                "message": f"Local Ollama models path is symlinked to {target}",
            })
            return status

        if local_dir.exists():
            if _has_files(local_dir):
                status["copied_items"] = _copy_contents(local_dir, drive_dir)
                backup_dir = local_dir.parent / "models_local_backup"
                if not backup_dir.exists():
                    local_dir.rename(backup_dir)
                    local_dir.symlink_to(drive_dir, target_is_directory=True)
                    status.update({
                        "ok": True,
                        "mode": "migrated_existing_local_models",
                        "backup_dir": str(backup_dir),
                        "message": "Existing local Ollama models were copied to Drive, backed up, and replaced by a symlink.",
                    })
                    return status
                status.update({
                    "ok": False,
                    "mode": "local_models_not_symlinked",
                    "backup_dir": str(backup_dir),
                    "message": "Local Ollama models exist and backup already exists; leaving files untouched to avoid data loss.",
                })
                return status
            local_dir.rmdir()

        local_dir.symlink_to(drive_dir, target_is_directory=True)
        status.update({
            "ok": True,
            "mode": "created_symlink",
            "message": "Created Drive-backed symlink for Ollama models.",
        })
        return status
    except Exception as exc:
        status.update({
            "ok": False,
            "mode": "error",
            "message": f"Ollama persistence setup failed: {type(exc).__name__}: {exc}",
        })
        return status
