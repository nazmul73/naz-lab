"""Scan Naz Lab backend queues and package folders.

Usage from repo root:

    python backend_adapters/scan_backend_queues.py

This script performs lightweight validation only. It does not run generation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.backend_queue import scan_backend_queues  # noqa: E402


def main() -> None:
    report = scan_backend_queues(limit_per_folder=100)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
