"""Safe JSON helpers for Naz Lab.

The project writes shared state from multiple Colab workstations. These helpers
reduce the risk of corrupted JSON by using a lock file, writing to a temporary
file first, then atomically replacing the target file.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Mapping


def safe_read_json(path: str | Path, default_data: Any) -> Any:
    """Read JSON safely.

    If the file is missing, return default_data. If the file is corrupted,
    rename it to a timestamped backup and return default_data.
    """

    target = Path(path)
    if not target.exists():
        return default_data

    try:
        with target.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        backup = target.with_suffix(target.suffix + f".corrupt_{int(time.time())}.bak")
        target.rename(backup)
        return default_data


def safe_write_json(path: str | Path, data: Any, lock_timeout: int = 20) -> None:
    """Write JSON safely with lock + temp write + replace.

    Safe JSON Write Rule:
    Read -> Lock -> Temp Write -> Rename -> Cleanup
    """

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    lock_path = target.with_suffix(target.suffix + ".lock")
    temp_path = target.with_suffix(target.suffix + ".tmp")

    started_at = time.time()
    while lock_path.exists():
        if time.time() - started_at > lock_timeout:
            raise TimeoutError(f"Timed out waiting for JSON lock: {lock_path}")
        time.sleep(0.25)

    try:
        lock_path.write_text(str(time.time()), encoding="utf-8")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        temp_path.replace(target)
    finally:
        if lock_path.exists():
            lock_path.unlink()


def append_output_log(
    log_path: str | Path,
    workstation: str,
    event: str,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Append one structured event to output_log.json."""

    target = Path(log_path)
    data = safe_read_json(target, {"logs": []})
    data.setdefault("logs", [])

    entry = {
        "timestamp": time.ctime(),
        "workstation": workstation,
        "event": event,
        "details": dict(details or {}),
    }
    data["logs"].append(entry)
    safe_write_json(target, data)
    return entry


def update_workstation_status(
    config_path: str | Path,
    workstation_name: str,
    updates: Mapping[str, Any],
) -> dict[str, Any]:
    """Merge updates into one workstation entry inside workstation_links.json."""

    target = Path(config_path)
    data = safe_read_json(target, {})
    current = data.get(workstation_name, {})
    current.update(dict(updates))
    current["last_updated"] = time.ctime()
    data[workstation_name] = current
    safe_write_json(target, data)
    return current
