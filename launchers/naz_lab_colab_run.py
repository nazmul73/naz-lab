"""Permanent one-line Colab launcher for Naz Lab.

Usage in a Colab Python cell:

!wget -q -O /content/naz_lab_colab_run.py https://raw.githubusercontent.com/nazmul73/naz-lab/main/launchers/naz_lab_colab_run.py && python /content/naz_lab_colab_run.py

Optional GPU image dependencies:

NAZLAB_INSTALL_IMAGE_DEPS=1 python /content/naz_lab_colab_run.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

try:
    from google.colab import drive, output  # type: ignore
except Exception:  # pragma: no cover - only available in Colab
    drive = None
    output = None

REPO_ZIP_URL = "https://github.com/nazmul73/naz-lab/archive/refs/heads/main.zip"
REPO_DIR = Path("/content/naz-lab")
ZIP_PATH = Path("/content/naz-lab-main.zip")
EXTRACTED_DIR = Path("/content/naz-lab-main")
BASE = Path("/content/drive/MyDrive/NazLab")
PORT = int(os.environ.get("NAZLAB_PORT", "8502"))
LOG = Path("/content/streamlit_naz_lab_runtime.log")
INSTALL_IMAGE_DEPS = os.environ.get("NAZLAB_INSTALL_IMAGE_DEPS", "0") == "1"

MINIMAL_DEPS = ["streamlit>=1.30", "requests", "Pillow", "watchdog"]
IMAGE_DEPS = ["diffusers", "torch", "transformers", "accelerate"]

DRIVE_FOLDERS = [
    BASE / "models",
    BASE / "models" / "ollama",
    BASE / "text_outputs",
    BASE / "chat_outputs",
    BASE / "script_outputs",
    BASE / "image_prompts",
    BASE / "image_outputs",
    BASE / "voice_outputs",
    BASE / "voice_outputs" / "reference_audio",
    BASE / "video_outputs",
    BASE / "job_queue",
    BASE / "job_queue" / "image_jobs",
    BASE / "job_queue" / "voice_jobs",
    BASE / "job_queue" / "video_jobs",
    BASE / "social_review",
    BASE / "final_packages",
    BASE / "final_packages" / "exports",
    BASE / "final_packages" / "drafts",
    BASE / "reference_images",
    BASE / "config",
    BASE / "logs",
]

COMPILE_TARGETS = [
    "master_dashboard/naz_lab_dashboard_v12.py",
    "master_dashboard/naz_lab_nav.py",
    "master_dashboard/naz_lab_home_panel.py",
    "master_dashboard/naz_lab_text_panel.py",
    "master_dashboard/naz_lab_voice_panel.py",
    "master_dashboard/naz_lab_image_panel.py",
    "master_dashboard/naz_lab_review_panel.py",
    "master_dashboard/naz_lab_facebook_panel.py",
    "master_dashboard/naz_lab_video_panel.py",
    "master_dashboard/naz_lab_files_panel.py",
    "master_dashboard/naz_lab_health_panel.py",
    "master_dashboard/naz_lab_runbook_panel.py",
    "master_dashboard/app_main.py",
    "master_dashboard/app_official.py",
    "voice_workstation/voice_backend.py",
    "social_agent/facebook_graph_backend.py",
    "shared/model_policy.py",
    "shared/ollama_persistence.py",
    "shared/ollama_text_generation.py",
    "shared/text_workstation_helpers.py",
    "shared/text_pipeline.py",
    "scripts/ollama_colab_runtime.py",
]


def run(cmd: list[str], *, check: bool = True, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, cwd=str(cwd) if cwd else None, text=True)


def safe_mkdir(path: Path) -> None:
    try:
        if path.exists() or path.is_symlink():
            if path.is_dir() or path.is_symlink():
                print("OK exists:", path)
                return
            backup = path.with_name(f"{path.name}_file_backup_{int(time.time())}")
            path.rename(backup)
            print("Backed up file conflict:", path, "->", backup)
        path.mkdir(parents=True, exist_ok=True)
        print("Created:", path)
    except FileExistsError:
        print("OK already exists or Drive race tolerated:", path)
    except Exception as exc:
        print("WARNING:", path, type(exc).__name__, exc)


def mount_drive() -> None:
    print("STEP 1/7: Mounting Google Drive")
    if drive is None:
        raise RuntimeError("This launcher is intended for Google Colab.")
    drive.mount("/content/drive", force_remount=False)


def prepare_drive() -> None:
    print("STEP 2/7: Preparing NazLab Drive folders")
    for folder in DRIVE_FOLDERS:
        safe_mkdir(folder)
    os.environ["OLLAMA_MODELS"] = str(BASE / "models" / "ollama")
    print("Drive ready:", BASE)


def download_repo() -> None:
    print("STEP 3/7: Downloading latest main branch")
    for path in [REPO_DIR, EXTRACTED_DIR]:
        if path.exists():
            shutil.rmtree(path)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    run(["wget", "-q", "-O", str(ZIP_PATH), REPO_ZIP_URL])
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall("/content")
    EXTRACTED_DIR.rename(REPO_DIR)
    print("Repo ready:", REPO_DIR)


def install_requirements() -> None:
    print("STEP 4/7: Installing runtime dependencies")
    deps = MINIMAL_DEPS + (IMAGE_DEPS if INSTALL_IMAGE_DEPS else [])
    run([sys.executable, "-m", "pip", "install", "-q", *deps], check=False)
    if INSTALL_IMAGE_DEPS:
        print("Requirements ready: minimal + image generation deps")
    else:
        print("Requirements ready: minimal dashboard deps")
        print("Tip: set NAZLAB_INSTALL_IMAGE_DEPS=1 before running this launcher for real GPU image generation dependencies.")


def run_ollama_helper() -> None:
    print("STEP 5/7: Running Ollama helper if available")
    helper = REPO_DIR / "scripts" / "ollama_colab_runtime.py"
    if helper.exists():
        run([sys.executable, str(helper)], check=False)
    else:
        print("SKIP: Ollama helper missing. Dashboard can open; generation may fallback.")


def validate_python_files() -> None:
    print("STEP 6/7: Running smoke check and py_compile validation")
    smoke = REPO_DIR / "scripts" / "backend_smoke_check.py"
    if smoke.exists():
        run([sys.executable, str(smoke)], check=False)
    for relative in COMPILE_TARGETS:
        target = REPO_DIR / relative
        if not target.exists():
            print("SKIP missing:", relative)
            continue
        result = subprocess.run([sys.executable, "-m", "py_compile", str(target)], capture_output=True, text=True)
        print(("PASS" if result.returncode == 0 else "FAIL"), relative)
        if result.returncode != 0:
            print(result.stderr)
            raise RuntimeError(f"py_compile failed: {target}")
    print("Validation ready")


def launch_dashboard() -> None:
    print("STEP 7/7: Launching official dashboard")
    app = REPO_DIR / "master_dashboard" / "app_official.py"
    subprocess.run("pkill -f streamlit || true", shell=True, check=False)
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app),
        "--server.port",
        str(PORT),
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",
        "--server.enableCORS",
        "false",
        "--server.enableXsrfProtection",
        "false",
    ]
    with open(LOG, "w", encoding="utf-8") as log_file:
        subprocess.Popen(cmd, stdout=log_file, stderr=log_file, cwd=str(REPO_DIR / "master_dashboard"), env=os.environ.copy())
    time.sleep(8)
    print("NAZ LAB RUNTIME READY")
    print("Opening Colab proxy window on port", PORT)
    print("Log file:", LOG)
    if output is not None:
        output.serve_kernel_port_as_window(PORT)
    else:
        print(f"Open Colab port proxy for {PORT} manually.")


def main() -> None:
    mount_drive()
    prepare_drive()
    download_repo()
    install_requirements()
    run_ollama_helper()
    validate_python_files()
    launch_dashboard()


if __name__ == "__main__":
    main()
