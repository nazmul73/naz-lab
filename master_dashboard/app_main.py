"""Naz Lab official main app entrypoint.

The full dashboard implementation lives in master_dashboard/naz_lab_dashboard_v12.py.
This wrapper keeps the stable official path for launchers and Colab tests.
"""

from __future__ import annotations

from naz_lab_dashboard_v12 import main


if __name__ == "__main__":
    main()
