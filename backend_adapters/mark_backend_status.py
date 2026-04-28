"""Mark backend status on a Naz Lab package JSON file.

Usage from repo root:

    python backend_adapters/mark_backend_status.py PACKAGE.json ready_for_backend "Ready for backend"

This script only updates package metadata. It does not run generation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.backend_status import mark_backend_status  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Safely mark backend status on a Naz Lab package JSON file.")
    parser.add_argument("package_path", help="Path to package/job JSON file.")
    parser.add_argument("status", help="Backend status to set, e.g. ready_for_backend, blocked, failed, completed.")
    parser.add_argument("message", help="Status update message to append to backend_events.")
    parser.add_argument("--allow-any-transition", action="store_true", help="Allow status change from any current status.")
    args = parser.parse_args()

    data = mark_backend_status(
        package_path=Path(args.package_path),
        next_status=args.status,
        message=args.message,
        allow_any_transition=args.allow_any_transition,
    )
    print(json.dumps({"ok": True, "path": args.package_path, "backend_status": data.get("backend_status"), "backend_last_updated": data.get("backend_last_updated")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
