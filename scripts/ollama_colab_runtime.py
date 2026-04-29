"""Colab Ollama runtime helper for Naz Lab.

Installs Ollama if needed, starts the server, waits with polling instead of a
fixed sleep, and pulls approved Text Builder models with clear progress output.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

OLLAMA_MODELS = Path("/content/drive/MyDrive/NazLab/models/ollama")
OLLAMA_LOG = Path("/content/ollama_naz_lab.log")
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
MODELS_TO_PULL = ["gemma2:2b", "qwen2.5:1.5b"]


def run(command: list[str] | str, *, shell: bool = False, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    print("RUN:", command if isinstance(command, str) else " ".join(command))
    result = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=timeout, check=False)
    if result.stdout.strip():
        print(result.stdout[-2000:])
    if result.stderr.strip():
        print(result.stderr[-2000:])
    return result


def find_ollama() -> str | None:
    for candidate in [shutil.which("ollama"), "/usr/local/bin/ollama", "/usr/bin/ollama", "/bin/ollama", "/root/.ollama/bin/ollama"]:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def install_ollama_if_needed() -> str | None:
    ollama = find_ollama()
    if ollama:
        print("Ollama found:", ollama)
        return ollama
    print("Ollama not found. Installing Ollama. This may take a minute...")
    run("curl -fsSL https://ollama.com/install.sh -o /content/install_ollama.sh", shell=True, timeout=180)
    run("bash /content/install_ollama.sh", shell=True, timeout=360)
    ollama = find_ollama()
    if ollama:
        print("Ollama installed:", ollama)
    else:
        print("WARNING: Ollama binary was not found after install attempt.")
    return ollama


def wait_for_ollama_ready(seconds: int = 60) -> bool:
    for i in range(seconds):
        result = run("curl -s http://localhost:11434/api/tags", shell=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            print(f"Ollama server ready after {i + 1}s")
            return True
        time.sleep(1)
    print("WARNING: Ollama server did not become ready in time.")
    if OLLAMA_LOG.exists():
        print("Last Ollama log lines:")
        print(OLLAMA_LOG.read_text(errors="ignore")[-3000:])
    return False


def start_ollama(ollama_bin: str | None) -> bool:
    if not ollama_bin:
        return False
    OLLAMA_MODELS.mkdir(parents=True, exist_ok=True)
    os.environ["OLLAMA_MODELS"] = str(OLLAMA_MODELS)
    run("pkill -f 'ollama serve' || true", shell=True)
    log_handle = OLLAMA_LOG.open("w")
    subprocess.Popen([ollama_bin, "serve"], stdout=log_handle, stderr=log_handle, env=os.environ.copy())
    return wait_for_ollama_ready(60)


def pull_models(ollama_bin: str | None) -> None:
    if not ollama_bin:
        print("SKIP model pull: Ollama is unavailable.")
        return
    for model in MODELS_TO_PULL:
        print(f"Downloading/checking {model}. First run can take several minutes; please wait...")
        result = run([ollama_bin, "pull", model], timeout=1800)
        print(f"Model {model}: {'OK' if result.returncode == 0 else 'CHECK LOG'}")
    run([ollama_bin, "list"], timeout=30)


def main() -> None:
    OLLAMA_MODELS.mkdir(parents=True, exist_ok=True)
    os.environ["OLLAMA_MODELS"] = str(OLLAMA_MODELS)
    ollama_bin = install_ollama_if_needed()
    if start_ollama(ollama_bin):
        pull_models(ollama_bin)
    else:
        print("Dashboard can still open, but Ollama generation may use safe template fallback.")


if __name__ == "__main__":
    main()
