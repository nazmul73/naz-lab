"""Naz Lab model health/status and missing-model helper.

Safe for Colab. Does not require GPU. Uses Ollama CLI/API when available.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import LOGS_DIR, OLLAMA_MODELS  # noqa: E402
from shared.job_queue_schema import write_json  # noqa: E402

MODEL_HEALTH_JSON = LOGS_DIR / "model_health_status.json"
RECOMMENDED_MODELS = {
    "cpu_recommended": "qwen2.5:1.5b",
    "cpu_emergency": "qwen2.5:0.5b",
    "gpu_recommended": "gemma2:2b",
    "gpu_optional": "qwen2.5:3b",
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ollama_binary() -> str:
    return shutil.which("ollama") or ""


def ollama_api_tags() -> dict[str, Any]:
    try:
        with urlopen("http://localhost:11434/api/tags", timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc), "models": []}


def installed_models() -> list[str]:
    tags = ollama_api_tags()
    if isinstance(tags, dict) and isinstance(tags.get("models"), list):
        return [item.get("name", "") for item in tags["models"] if isinstance(item, dict) and item.get("name")]
    return []


def model_present(model: str, names: list[str] | None = None) -> bool:
    names = names or installed_models()
    return any(name == model or name.startswith(f"{model}:") for name in names)


def build_model_health() -> dict[str, Any]:
    names = installed_models()
    status = {
        "generated_at": now_iso(),
        "ollama_binary": ollama_binary(),
        "ollama_models_path": str(OLLAMA_MODELS),
        "installed_models": names,
        "recommended_models": RECOMMENDED_MODELS,
        "availability": {key: {"model": model, "installed": model_present(model, names)} for key, model in RECOMMENDED_MODELS.items()},
        "pull_commands": {key: f"ollama pull {model}" for key, model in RECOMMENDED_MODELS.items()},
    }
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    write_json(MODEL_HEALTH_JSON, status)
    return status


def pull_missing_models(models: list[str] | None = None) -> dict[str, Any]:
    selected = models or [RECOMMENDED_MODELS["cpu_recommended"], RECOMMENDED_MODELS["cpu_emergency"]]
    binary = ollama_binary()
    results: list[dict[str, Any]] = []
    if not binary:
        return {"ok": False, "message": "ollama binary not found", "results": []}
    current = installed_models()
    for model in selected:
        if model_present(model, current):
            results.append({"model": model, "status": "already_installed"})
            continue
        proc = subprocess.run([binary, "pull", model], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        results.append({"model": model, "status": "pulled" if proc.returncode == 0 else "failed", "returncode": proc.returncode, "output_tail": (proc.stdout or "")[-2000:]})
    health = build_model_health()
    return {"ok": True, "generated_at": now_iso(), "results": results, "health": health}


if __name__ == "__main__":
    print(json.dumps(build_model_health(), ensure_ascii=False, indent=2))
