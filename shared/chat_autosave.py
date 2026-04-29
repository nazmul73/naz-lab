"""Drive-backed incremental chat autosave helpers for Naz Lab.

The dashboard may lose Streamlit session state after a Colab restart. These
helpers persist each chat-style exchange as JSONL plus a small metadata file so
casual chat tests and future conversation sessions can be recovered from Drive.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from shared.drive_paths import CHAT_OUTPUTS

CHAT_SESSIONS_DIR = CHAT_OUTPUTS / "sessions"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def new_chat_session_id(prefix: str = "text_chat") -> str:
    return f"{prefix}_{now_stamp()}_{uuid.uuid4().hex[:8]}"


def ensure_chat_session(session_id: str | None = None) -> dict[str, str]:
    CHAT_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sid = session_id or new_chat_session_id()
    jsonl_path = CHAT_SESSIONS_DIR / f"{sid}.jsonl"
    metadata_path = CHAT_SESSIONS_DIR / f"{sid}.metadata.json"
    if not metadata_path.exists():
        metadata = {
            "session_id": sid,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "jsonl_path": str(jsonl_path),
            "source": "naz_lab_text_builder",
        }
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"session_id": sid, "jsonl_path": str(jsonl_path), "metadata_path": str(metadata_path)}


def append_chat_turn(
    *,
    session_id: str,
    user_message: str,
    assistant_message: str,
    mode: str,
    language: str,
    model: str,
    engine_status: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, str]:
    session = ensure_chat_session(session_id)
    jsonl_path = Path(session["jsonl_path"])
    metadata_path = Path(session["metadata_path"])
    record = {
        "timestamp": now_iso(),
        "session_id": session["session_id"],
        "mode": mode,
        "language": language,
        "model": model,
        "engine_status": engine_status,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "extra": extra or {},
    }
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    metadata = {
        "session_id": session["session_id"],
        "created_at": None,
        "updated_at": now_iso(),
        "jsonl_path": str(jsonl_path),
        "source": "naz_lab_text_builder",
        "last_mode": mode,
        "last_language": language,
        "last_model": model,
    }
    if metadata_path.exists():
        try:
            old = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["created_at"] = old.get("created_at") or now_iso()
        except Exception:
            metadata["created_at"] = now_iso()
    else:
        metadata["created_at"] = now_iso()
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return session
