"""Ollama model persistence helpers for Naz Lab Colab runtimes.

The goal is to keep downloaded Ollama models on Google Drive and expose them
through the default local Ollama model path after a Colab restart. The helper is
safe to call repeatedly from Streamlit panels or launchers and avoids crashing on
Google Drive file/symlink race conditions.
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Any

from shared.drive_paths import OLLAMA_MODELS

DEFAULT_LOCAL_OLLAMA_MODELS = Path.home() / ".ollama" / "models"


def _safe_mkdir(path: Path) -> tuple[bool, str]:
    """Create a directory without crashing on Drive symlink/file conflicts."""
    try:
        if path.exists() or path.is_symlink():
            if path.is_dir() or path.is_symlink():
                return True, "exists"
            backup = path.with_name(f"{path.name}_file_backup_{int(time.time())}")
            path.rename(backup)
            path.mkdir(parents=True, exist_ok=True)
            return True, f"file_conflict_backed_up_to:{backup}"
        path.mkdir(parents=True, exist_ok=True)
        return True, "created"
    except FileExistsError:
        return True, "exists_file_race_tolerated"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _has_files(path: Path) -> bool:
    try:
        return path.exists() and any(path.iterdir())
    except Exception:
        return False


def _copy_contents(src: Path, dst: Path) -> int:
    copied = 0
    _safe_mkdir(dst)
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


def _replace_with_symlink(local_dir: Path, drive_dir: Path, status: dict[str, Any], mode: str) -> dict[str, Any]:
    """Replace local model directory with a symlink to Drive when safe."""
    if local_dir.is_symlink():
        target = local_dir.resolve()
        status.update({"ok": target == drive_dir.resolve(), "mode": "already_symlinked", "message": f"Local Ollama models path is symlinked to {target}"})
        return status

    if local_dir.exists():
        if _has_files(local_dir):
            backup_dir = local_dir.parent / "models_local_backup"
            if backup_dir.exists():
                backup_dir = local_dir.parent / f"models_local_backup_{int(time.time())}"
            local_dir.rename(backup_dir)
            status["backup_dir"] = str(backup_dir)
        else:
            local_dir.rmdir()

    local_dir.symlink_to(drive_dir, target_is_directory=True)
    status.update({"ok": True, "mode": mode, "message": "Local Ollama models path now points to the Drive-backed model store."})
    return status


def ensure_ollama_persistence(
    drive_models_dir: Path = OLLAMA_MODELS,
    local_models_dir: Path | None = None,
) -> dict[str, Any]:
    """Ensure Ollama models persist through Drive-backed storage.

    Returns a status dictionary that can be displayed in Health/Text panels.
    It never raises for normal filesystem conflicts; failures are reported in
    the returned status so the UI can remain stable.
    """

    local_dir = local_models_dir or DEFAULT_LOCAL_OLLAMA_MODELS
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
        drive_ok, drive_msg = _safe_mkdir(drive_dir)
        parent_ok, parent_msg = _safe_mkdir(local_dir.parent)
        status["drive_mkdir"] = drive_msg
        status["local_parent_mkdir"] = parent_msg
        if not drive_ok or not parent_ok:
            status.update({"ok": False, "mode": "mkdir_failed", "message": f"Drive/local setup failed: {drive_msg}; {parent_msg}"})
            return status

        if local_dir.is_symlink():
            target = local_dir.resolve()
            status.update({
                "ok": target == drive_dir.resolve(),
                "mode": "already_symlinked",
                "message": f"Local Ollama models path is symlinked to {target}",
            })
            return status

        if local_dir.exists() and _has_files(local_dir):
            status["copied_items"] = _copy_contents(local_dir, drive_dir)
            return _replace_with_symlink(local_dir, drive_dir, status, "migrated_existing_local_models")

        return _replace_with_symlink(local_dir, drive_dir, status, "created_symlink")
    except Exception as exc:
        status.update({
            "ok": False,
            "mode": "error",
            "message": f"Ollama persistence setup failed: {type(exc).__name__}: {exc}",
        })
        return status
