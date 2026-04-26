"""Phase 0 foundation setup for Naz Lab.

Run this script in Google Colab after cloning the repository. It creates the
Naz Lab Drive structure, initializes shared JSON state, and prepares Ollama
model persistence by linking /root/.ollama/models to Google Drive.

This phase intentionally does NOT install Ollama or pull any model.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Allow running directly from /content/naz-lab/master_setup in Colab.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    CUSTOM_GEMS_JSON,
    OUTPUT_LOG_JSON,
    OLLAMA_MODELS,
    REQUIRED_DIRECTORIES,
    REQUIRED_JSON_FILES,
    TOOL_LINKS_JSON,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import append_output_log, safe_write_json  # noqa: E402


def running_in_colab() -> bool:
    """Return True when the script appears to be running inside Google Colab."""

    try:
        import google.colab  # type: ignore  # noqa: F401
        return True
    except Exception:
        return False


def mount_google_drive_if_needed() -> None:
    """Mount Google Drive when running in Colab."""

    if not running_in_colab():
        print("INFO: Not running in Colab; skipping drive.mount().")
        return

    if Path("/content/drive/MyDrive").exists():
        print("OK: Google Drive already mounted.")
        return

    from google.colab import drive  # type: ignore

    drive.mount("/content/drive")
    print("OK: Google Drive mounted.")


def create_directories() -> None:
    """Create the full Naz Lab Drive directory structure."""

    for directory in REQUIRED_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"OK DIR: {directory}")


def default_workstation_links() -> dict:
    now = time.ctime()
    base = {
        "status": "not_started",
        "public_url": "",
        "tunnel_type": "",
        "fixed_domain": "",
        "last_url_updated": "",
        "last_output_path": "",
        "last_updated": now,
    }
    return {
        "text_workstation": {**base, "phase": "Phase 1", "tunnel_type": "cloudflare_quick"},
        "master_dashboard": {**base, "phase": "Phase 2"},
        "image_workstation": {**base, "phase": "Phase 3"},
        "voice_workstation": {**base, "phase": "Phase 4"},
        "video_workstation": {**base, "phase": "Phase 5"},
        "face_workstation": {**base, "phase": "Phase 6"},
    }


def initialize_json_files() -> None:
    """Create default JSON state files if they do not exist."""

    defaults = {
        WORKSTATION_LINKS_JSON: default_workstation_links(),
        CUSTOM_GEMS_JSON: {"custom_gems": []},
        TOOL_LINKS_JSON: {
            "cloudflare_tunnel": {
                "primary": True,
                "notes": "Cloudflare quick tunnel is primary for testing. Named tunnel can be added later for fixed domain.",
            },
            "localtunnel": {
                "primary": False,
                "notes": "Fallback only. Not preferred due to possible Streamlit JavaScript loading issues.",
            },
            "ngrok": {
                "primary": False,
                "notes": "Optional if user has token saved in Colab Secrets.",
            },
        },
        OUTPUT_LOG_JSON: {"logs": []},
    }

    for path, data in defaults.items():
        if path.exists():
            print(f"EXISTS JSON: {path}")
            continue
        safe_write_json(path, data)
        print(f"CREATED JSON: {path}")


def verify_or_repair_ollama_symlink() -> bool:
    """Prepare /root/.ollama/models -> Drive models/ollama symlink."""

    OLLAMA_MODELS.mkdir(parents=True, exist_ok=True)

    local_ollama_dir = Path("/root/.ollama")
    local_models = local_ollama_dir / "models"
    local_ollama_dir.mkdir(parents=True, exist_ok=True)

    desired_target = str(OLLAMA_MODELS)

    if local_models.exists() or local_models.is_symlink():
        if local_models.is_symlink():
            current_target = os.readlink(local_models)
            if current_target == desired_target:
                print(f"OK SYMLINK: {local_models} -> {desired_target}")
                return True
            print(f"REPAIR SYMLINK: {local_models} pointed to {current_target}")
            local_models.unlink()
        else:
            print(f"REPAIR: removing local Ollama models path before symlink: {local_models}")
            if local_models.is_dir():
                import shutil

                shutil.rmtree(local_models)
            else:
                local_models.unlink()

    os.symlink(desired_target, local_models)
    print(f"CREATED SYMLINK: {local_models} -> {desired_target}")
    return True


def validate_phase_0() -> bool:
    """Check required folders and JSON files."""

    all_ok = True

    if not BASE_PATH.exists():
        print(f"MISSING BASE: {BASE_PATH}")
        all_ok = False

    for directory in REQUIRED_DIRECTORIES:
        if directory.exists() and directory.is_dir():
            print(f"OK VALID DIR: {directory}")
        else:
            print(f"MISSING DIR: {directory}")
            all_ok = False

    import json

    for json_file in REQUIRED_JSON_FILES:
        if not json_file.exists():
            print(f"MISSING JSON: {json_file}")
            all_ok = False
            continue
        try:
            with json_file.open("r", encoding="utf-8") as handle:
                json.load(handle)
            print(f"OK VALID JSON: {json_file}")
        except Exception as exc:
            print(f"BAD JSON: {json_file} | {exc}")
            all_ok = False

    local_models = Path("/root/.ollama/models")
    if local_models.is_symlink() and os.readlink(local_models) == str(OLLAMA_MODELS):
        print("OK VALID SYMLINK: Ollama persistence path is ready.")
    else:
        print("BAD SYMLINK: Ollama persistence path is not ready.")
        all_ok = False

    return all_ok


def main() -> None:
    print("Starting Naz Lab Phase 0 foundation setup...")
    mount_google_drive_if_needed()
    create_directories()
    initialize_json_files()
    verify_or_repair_ollama_symlink()

    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="foundation_setup",
        event="phase_0_setup_ran",
        details={"base_path": str(BASE_PATH)},
    )

    if validate_phase_0():
        print("PHASE 0 PASSED")
    else:
        print("PHASE 0 FAILED")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
