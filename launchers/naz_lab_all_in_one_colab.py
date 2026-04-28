"""Naz Lab all-in-one Colab launcher.

Default launches the latest official workflow dashboard:
- master_dashboard/app_official.py -> app_phase222.py

Set APP_REL to another app path when testing a specific phase.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

try:
    from google.colab import drive, output  # type: ignore
except Exception:  # pragma: no cover
    drive = None
    output = None

REPO_ZIP_URL = "https://github.com/nazmul73/naz-lab/archive/refs/heads/main.zip"
ZIP_PATH = Path("/content/naz-lab-main.zip")
EXTRACT_DIR = Path("/content/naz-lab-main")
REPO_DIR = Path("/content/naz-lab")
APP_REL = os.environ.get("NAZ_LAB_APP", "master_dashboard/app_official.py")
PORT = int(os.environ.get("NAZ_LAB_PORT", "8502"))
LOG_PATH = Path(f"/content/naz_lab_streamlit_{PORT}.log")
BASE_PATH = Path("/content/drive/MyDrive/NazLab")


def ensure_drive() -> None:
    if not Path("/content/drive/MyDrive").exists() and drive is not None:
        drive.mount("/content/drive")
    if not Path("/content/drive/MyDrive").exists():
        raise RuntimeError("Google Drive is not mounted.")


def ensure_repo() -> None:
    for path in [ZIP_PATH, EXTRACT_DIR, REPO_DIR]:
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()
    print("Downloading latest repo ZIP...")
    urllib.request.urlretrieve(REPO_ZIP_URL, ZIP_PATH)
    print("Extracting repo...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall("/content")
    EXTRACT_DIR.rename(REPO_DIR)


def ensure_dirs() -> None:
    for folder in [
        BASE_PATH / "text_outputs",
        BASE_PATH / "chat_outputs",
        BASE_PATH / "script_outputs",
        BASE_PATH / "image_prompts",
        BASE_PATH / "image_outputs",
        BASE_PATH / "job_queue" / "image_jobs",
        BASE_PATH / "job_queue" / "completed_jobs",
        BASE_PATH / "models" / "ollama",
        BASE_PATH / "config",
        BASE_PATH / "logs",
        BASE_PATH / "social_review",
        BASE_PATH / "final_packages",
        BASE_PATH / "reference_images",
    ]:
        folder.mkdir(parents=True, exist_ok=True)


def install_deps() -> None:
    packages = ["streamlit", "requests", "Pillow"]
    if "phase221" in APP_REL or "real_image" in APP_REL:
        packages += ["accelerate", "safetensors", "transformers", "diffusers"]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *packages], check=False)


def launch() -> None:
    os.chdir(REPO_DIR)
    app_path = REPO_DIR / APP_REL
    if not app_path.exists():
        raise RuntimeError(f"App not found: {app_path}")
    subprocess.run([sys.executable, "-m", "py_compile", str(app_path)], check=True)
    subprocess.run("pkill -f streamlit || true", shell=True, check=False)
    time.sleep(2)
    with LOG_PATH.open("w", encoding="utf-8") as log:
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", str(PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
        ], stdout=log, stderr=subprocess.STDOUT, cwd=str(REPO_DIR))
    time.sleep(8)
    print(LOG_PATH.read_text(encoding="utf-8", errors="ignore")[-3000:])
    if process.poll() is not None:
        raise RuntimeError(f"Streamlit exited early. Check {LOG_PATH}")
    print("NAZ LAB ALL-IN-ONE LAUNCHER READY")
    print("App:", APP_REL)
    print("Port:", PORT)
    if output is not None:
        output.serve_kernel_port_as_window(PORT)


def main() -> None:
    print("============================================================")
    print("Naz Lab All-in-One Launcher")
    print("============================================================")
    ensure_drive()
    ensure_repo()
    ensure_dirs()
    install_deps()
    launch()


if __name__ == "__main__":
    main()
