"""Naz Lab Master Dashboard official wrapper.

Current official main interface hub:
master_dashboard/app_main.py

The main hub interconnects active workstations, dashboards, launchers, Drive
folders, package flow, real image backend, and safety-gated social review.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.ollama_persistence import ensure_ollama_persistence
from shared.ollama_text_generation import call_ollama as policy_call_ollama

# Run before Streamlit imports the main hub so Colab restarts reuse Drive-backed
# Ollama models instead of silently falling back to a fresh local model folder.
os.environ.setdefault("NAZLAB_OLLAMA_PERSISTENCE_STATUS", str(ensure_ollama_persistence()))

# Patch the legacy Text Workstation backend before the dashboard imports panels.
# This keeps old helper functions available while replacing generation with the
# current model-specific prompt formatter, larger Bangla token limits, and safe
# approved-model fallback chain.
try:
    import text_workstation.app_phase110 as text_backend

    text_backend.call_ollama = policy_call_ollama
except Exception as exc:
    os.environ.setdefault("NAZLAB_TEXT_GENERATION_PATCH_WARNING", f"{type(exc).__name__}: {exc}")

from app_main import main


if __name__ == "__main__":
    main()
