"""Colab launcher for Naz Lab Phase 3.1 Real Image Backend.

Run after mounting Drive and loading the repo.
This installs GPU image dependencies, starts the Dashboard/Image backend flow,
and processes queued image jobs into real PNG images when CUDA is available.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_DIR = Path("/content/naz-lab")
APP_REL = "master_dashboard/app_phase221.py"
PORT = 8502
LOG_PATH = Path("/content/streamlit_dashboard_phase221.log")


def run(cmd: list[str] | str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=isinstance(cmd, str), check=check)


def main() -> None:
    if not REPO_DIR.exists():
        raise RuntimeError("Repo not found at /content/naz-lab. Load repo first.")
    os.chdir(REPO_DIR)
    print("Installing Phase 3.1 dependencies...")
    run([sys.executable, "-m", "pip", "install", "-q", "streamlit", "requests", "accelerate", "safetensors", "transformers", "diffusers", "Pillow"], check=False)
    print("Checking CUDA...")
    run([sys.executable, "-c", "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())"], check=False)
    print("Validating Dashboard Phase 2.21...")
    app_path = REPO_DIR / APP_REL
    run([sys.executable, "-m", "py_compile", str(app_path)], check=True)
    print("Stopping old Streamlit...")
    run("pkill -f streamlit || true", check=False)
    time.sleep(2)
    print("Starting Dashboard Phase 2.21 on port", PORT)
    with LOG_PATH.open("w", encoding="utf-8") as log:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", str(PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
        ], stdout=log, stderr=subprocess.STDOUT, cwd=str(REPO_DIR))
    time.sleep(8)
    print(LOG_PATH.read_text(encoding="utf-8", errors="ignore")[-3000:])
    print("NAZ LAB DASHBOARD PHASE 2.21 / REAL IMAGE BACKEND PHASE 3.1 READY")


if __name__ == "__main__":
    main()
