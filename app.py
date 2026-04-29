"""Naz Lab root launcher.

The official Naz Lab dashboard lives at:
    master_dashboard/app_official.py

This root file is intentionally a thin compatibility wrapper so older launchers
that run `streamlit run app.py` still open the official dashboard instead of a
separate legacy workstation.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
MASTER_DASHBOARD = REPO_ROOT / "master_dashboard"
for path in [REPO_ROOT, MASTER_DASHBOARD]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from master_dashboard.app_official import main


if __name__ == "__main__":
    main()
