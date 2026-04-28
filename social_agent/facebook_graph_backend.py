"""Naz Lab Facebook Graph API backend skeleton.

Safety model:
- No automatic posting by default.
- Requires approved job record from social_review/approved_jobs.json.
- Requires explicit manual confirmation flag in config.
- Token/page config is loaded from Drive config file, not hardcoded.

This module is implementation-ready for future API testing, but safe by default.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, CONFIG_DIR, LOGS_DIR  # noqa: E402
from shared.job_queue_schema import read_json, write_json  # noqa: E402

SOCIAL_REVIEW_DIR = BASE_PATH / "social_review"
APPROVED_JOBS_JSON = SOCIAL_REVIEW_DIR / "approved_jobs.json"
FACEBOOK_CONFIG_JSON = CONFIG_DIR / "facebook_graph_config.json"
SOCIAL_POST_LOG_JSON = LOGS_DIR / "social_post_log.json"

DEFAULT_CONFIG = {
    "enabled": False,
    "manual_approval_required": True,
    "dry_run": True,
    "page_id": "",
    "access_token_env": "FACEBOOK_PAGE_ACCESS_TOKEN",
    "graph_api_version": "v19.0",
    "notes": "Set enabled=true, dry_run=false, page_id, and env token only after manual approval testing.",
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_config() -> dict[str, Any]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    SOCIAL_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    if not FACEBOOK_CONFIG_JSON.exists():
        write_json(FACEBOOK_CONFIG_JSON, DEFAULT_CONFIG)
    if not SOCIAL_POST_LOG_JSON.exists():
        write_json(SOCIAL_POST_LOG_JSON, {"items": []})
    config = read_json(FACEBOOK_CONFIG_JSON, DEFAULT_CONFIG)
    if not isinstance(config, dict):
        config = DEFAULT_CONFIG.copy()
        write_json(FACEBOOK_CONFIG_JSON, config)
    return {**DEFAULT_CONFIG, **config}


def approved_items() -> list[dict[str, Any]]:
    data = read_json(APPROVED_JOBS_JSON, {"items": []})
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return [item for item in data["items"] if isinstance(item, dict)]
    return []


def compose_post_message(item: dict[str, Any]) -> str:
    topic = item.get("topic", "")
    prompt = item.get("prompt_preview", "")
    project = item.get("project", "Naz Lab")
    return f"{project}\n\n{topic}\n\n{prompt}".strip()


def log_event(event: dict[str, Any]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    data = read_json(SOCIAL_POST_LOG_JSON, {"items": []})
    items = data.get("items", []) if isinstance(data, dict) else []
    if not isinstance(items, list):
        items = []
    items.insert(0, {"at": now_iso(), **event})
    write_json(SOCIAL_POST_LOG_JSON, {"updated_at": now_iso(), "items": items[:500]})


def gated_post_to_facebook(review_id: str, *, manual_confirm: bool = False) -> dict[str, Any]:
    config = ensure_config()
    item = next((entry for entry in approved_items() if entry.get("review_id") == review_id or entry.get("job_id") == review_id), None)
    if not item:
        result = {"ok": False, "reason": "approved item not found", "review_id": review_id}
        log_event({"event": "post_blocked", **result})
        return result
    if not config.get("enabled"):
        result = {"ok": False, "reason": "facebook backend disabled", "config_path": str(FACEBOOK_CONFIG_JSON)}
        log_event({"event": "post_blocked", "review_id": review_id, **result})
        return result
    if config.get("manual_approval_required", True) and not manual_confirm:
        result = {"ok": False, "reason": "manual confirmation required", "review_id": review_id}
        log_event({"event": "post_blocked", **result})
        return result
    message = compose_post_message(item)
    if config.get("dry_run", True):
        result = {"ok": True, "dry_run": True, "review_id": review_id, "message_preview": message[:1000]}
        log_event({"event": "dry_run_post", **result})
        return result
    page_id = str(config.get("page_id", "")).strip()
    token = os.environ.get(str(config.get("access_token_env", "FACEBOOK_PAGE_ACCESS_TOKEN")), "")
    version = str(config.get("graph_api_version", "v19.0")).strip() or "v19.0"
    if not page_id or not token:
        result = {"ok": False, "reason": "missing page_id or access token env"}
        log_event({"event": "post_blocked", "review_id": review_id, **result})
        return result
    url = f"https://graph.facebook.com/{version}/{page_id}/feed"
    body = urlencode({"message": message, "access_token": token}).encode("utf-8")
    req = Request(url, data=body, method="POST")
    try:
        with urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result = {"ok": True, "dry_run": False, "review_id": review_id, "graph_response": payload}
        log_event({"event": "posted", **result})
        return result
    except Exception as exc:
        result = {"ok": False, "reason": str(exc), "review_id": review_id}
        log_event({"event": "post_failed", **result})
        return result


if __name__ == "__main__":
    print(json.dumps({"config": ensure_config(), "approved_count": len(approved_items()), "note": "Use gated_post_to_facebook(review_id, manual_confirm=True) only after manual approval."}, ensure_ascii=False, indent=2))
