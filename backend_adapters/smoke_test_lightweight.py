"""Naz Lab lightweight smoke test.

This script checks that lightweight backend adapters, shared backend helpers, and
key Streamlit apps compile/import without running heavy generation tools.

Usage from repo root:

    python backend_adapters/smoke_test_lightweight.py
"""

from __future__ import annotations

import importlib
import json
import py_compile
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

COMPILE_TARGETS = [
    "master_dashboard/app.py",
    "text_workstation/app.py",
    "image_workstation/app.py",
    "voice_workstation/app.py",
    "video_workstation/app.py",
    "portrait_workstation/app.py",
    "project_workstation/app.py",
    "backend_adapters/create_backend_package.py",
    "backend_adapters/final_reel_pack_assembler.py",
    "backend_adapters/generic_tts_adapter.py",
    "backend_adapters/generic_tts_gtts_adapter.py",
    "backend_adapters/image_adapter.py",
    "backend_adapters/image_placeholder_adapter.py",
    "backend_adapters/mark_backend_status.py",
    "backend_adapters/portrait_adapter.py",
    "backend_adapters/scan_backend_queues.py",
    "backend_adapters/video_adapter.py",
    "backend_adapters/video_placeholder_adapter.py",
    "shared/backend_queue.py",
    "shared/backend_schema.py",
    "shared/backend_status.py",
    "shared/backend_validation.py",
    "shared/reference_asset_policy.py",
]

IMPORT_TARGETS = [
    "shared.backend_schema",
    "shared.backend_validation",
    "shared.backend_status",
    "shared.backend_queue",
    "shared.reference_asset_policy",
    "backend_adapters.generic_tts_adapter",
    "backend_adapters.generic_tts_gtts_adapter",
    "backend_adapters.image_adapter",
    "backend_adapters.image_placeholder_adapter",
    "backend_adapters.video_adapter",
    "backend_adapters.video_placeholder_adapter",
    "backend_adapters.portrait_adapter",
    "backend_adapters.final_reel_pack_assembler",
]


def compile_targets() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rel_path in COMPILE_TARGETS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            results.append({"target": rel_path, "ok": False, "error": "missing file"})
            continue
        try:
            py_compile.compile(str(path), doraise=True)
            results.append({"target": rel_path, "ok": True})
        except Exception as exc:
            results.append({"target": rel_path, "ok": False, "error": str(exc)})
    return results


def import_targets() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for module_name in IMPORT_TARGETS:
        try:
            importlib.import_module(module_name)
            results.append({"target": module_name, "ok": True})
        except Exception as exc:
            results.append({"target": module_name, "ok": False, "error": str(exc)})
    return results


def main() -> None:
    compile_results = compile_targets()
    import_results = import_targets()
    all_results = compile_results + import_results
    ok = all(item.get("ok") is True for item in all_results)
    report = {
        "ok": ok,
        "compile_total": len(compile_results),
        "import_total": len(import_results),
        "failed": [item for item in all_results if item.get("ok") is not True],
        "compile_results": compile_results,
        "import_results": import_results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
