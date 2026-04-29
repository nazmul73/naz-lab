"""Naz Lab backend smoke check for Colab/runtime validation.

This script avoids installing system software. It validates Drive folders,
Python imports, Text Builder model policy, Ollama visibility when already
installed, and py_compile status for official backend/dashboard modules.

Legacy text_workstation/app_phase110.py is intentionally not part of official
runtime validation.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_DIR = Path("/content/naz-lab")
BASE_DIR = Path("/content/drive/MyDrive/NazLab")
DRIVE_OLLAMA_MODELS = BASE_DIR / "models" / "ollama"
LOCAL_OLLAMA_MODELS = Path.home() / ".ollama" / "models"

DRIVE_FOLDERS = [
    BASE_DIR / "models",
    DRIVE_OLLAMA_MODELS,
    BASE_DIR / "text_outputs",
    BASE_DIR / "chat_outputs",
    BASE_DIR / "script_outputs",
    BASE_DIR / "image_prompts",
    BASE_DIR / "image_outputs",
    BASE_DIR / "voice_outputs",
    BASE_DIR / "voice_outputs" / "reference_audio",
    BASE_DIR / "video_outputs",
    BASE_DIR / "job_queue",
    BASE_DIR / "job_queue" / "image_jobs",
    BASE_DIR / "job_queue" / "voice_jobs",
    BASE_DIR / "job_queue" / "video_jobs",
    BASE_DIR / "social_review",
    BASE_DIR / "final_packages",
    BASE_DIR / "final_packages" / "exports",
    BASE_DIR / "reference_images",
    BASE_DIR / "config",
    BASE_DIR / "logs",
]

COMPILE_TARGETS = [
    REPO_DIR / "master_dashboard" / "naz_lab_dashboard_v12.py",
    REPO_DIR / "master_dashboard" / "naz_lab_nav.py",
    REPO_DIR / "master_dashboard" / "naz_lab_text_panel.py",
    REPO_DIR / "master_dashboard" / "naz_lab_voice_panel.py",
    REPO_DIR / "master_dashboard" / "naz_lab_image_panel.py",
    REPO_DIR / "master_dashboard" / "naz_lab_review_panel.py",
    REPO_DIR / "master_dashboard" / "naz_lab_facebook_panel.py",
    REPO_DIR / "master_dashboard" / "app_main.py",
    REPO_DIR / "master_dashboard" / "app_official.py",
    REPO_DIR / "voice_workstation" / "voice_backend.py",
    REPO_DIR / "social_agent" / "facebook_graph_backend.py",
    REPO_DIR / "shared" / "model_policy.py",
    REPO_DIR / "shared" / "ollama_persistence.py",
    REPO_DIR / "shared" / "ollama_text_generation.py",
    REPO_DIR / "shared" / "text_workstation_helpers.py",
    REPO_DIR / "shared" / "text_pipeline.py",
    REPO_DIR / "scripts" / "ollama_colab_runtime.py",
]


def safe_mkdir(path: Path) -> None:
    """Create a directory without crashing on Drive symlink/file conflicts."""
    try:
        if path.exists() or path.is_symlink():
            if path.is_dir() or path.is_symlink():
                print(f"OK exists: {path}")
                return
            backup = path.with_name(f"{path.name}_file_backup_{int(time.time())}")
            path.rename(backup)
            print(f"Backed up file conflict: {path} -> {backup}")
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created: {path}")
    except FileExistsError:
        print(f"OK already exists or Drive conflict tolerated: {path}")
    except Exception as exc:
        print(f"WARNING could not create {path}: {type(exc).__name__}: {exc}")


def ensure_drive_folders() -> None:
    for folder in DRIVE_FOLDERS:
        safe_mkdir(folder)


def ensure_ollama_env() -> dict[str, str | bool]:
    os.environ["OLLAMA_MODELS"] = str(DRIVE_OLLAMA_MODELS)
    safe_mkdir(DRIVE_OLLAMA_MODELS)
    safe_mkdir(LOCAL_OLLAMA_MODELS.parent)
    if LOCAL_OLLAMA_MODELS.is_symlink():
        return {"ok": True, "mode": "already_symlinked", "target": str(LOCAL_OLLAMA_MODELS.resolve())}
    if LOCAL_OLLAMA_MODELS.exists():
        return {"ok": True, "mode": "env_only_existing_local_dir", "OLLAMA_MODELS": str(DRIVE_OLLAMA_MODELS)}
    try:
        LOCAL_OLLAMA_MODELS.symlink_to(DRIVE_OLLAMA_MODELS, target_is_directory=True)
        return {"ok": True, "mode": "created_symlink", "target": str(DRIVE_OLLAMA_MODELS)}
    except Exception as exc:
        return {"ok": False, "mode": "symlink_failed", "error": f"{type(exc).__name__}: {exc}", "OLLAMA_MODELS": str(DRIVE_OLLAMA_MODELS)}


def py_compile_targets() -> None:
    for target in COMPILE_TARGETS:
        if not target.exists():
            print(f"SKIP missing: {target}")
            continue
        result = subprocess.run([sys.executable, "-m", "py_compile", str(target)], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"PASS py_compile: {target.relative_to(REPO_DIR)}")
        else:
            print(f"FAIL py_compile: {target.relative_to(REPO_DIR)}")
            print(result.stderr)
            raise RuntimeError(f"py_compile failed: {target}")


def print_model_policy() -> None:
    if str(REPO_DIR) not in sys.path:
        sys.path.insert(0, str(REPO_DIR))
    from shared.model_policy import model_policy_status

    print("MODEL POLICY:", model_policy_status())


def print_backend_policy() -> None:
    print("BACKEND POLICY:", {
        "generation_backend": "shared.ollama_text_generation.call_ollama",
        "helper_backend": "shared.text_workstation_helpers",
        "legacy_app_phase110_active": False,
    })


def print_ollama_status() -> None:
    ollama_path = shutil.which("ollama")
    print("OLLAMA_BINARY:", ollama_path or "not found")
    if ollama_path:
        result = subprocess.run([ollama_path, "--version"], capture_output=True, text=True)
        print("OLLAMA_VERSION:", (result.stdout or result.stderr).strip())


def main() -> None:
    print("NAZ LAB BACKEND SMOKE CHECK START")
    ensure_drive_folders()
    print("OLLAMA_ENV:", ensure_ollama_env())
    print_model_policy()
    print_backend_policy()
    print_ollama_status()
    py_compile_targets()
    print("NAZ LAB BACKEND SMOKE CHECK READY")


if __name__ == "__main__":
    main()
