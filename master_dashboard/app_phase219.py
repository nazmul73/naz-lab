"""Naz Lab Master Dashboard Phase 2.19.

Adds backend/frontend coverage for items 21-30:
- model health/status JSON
- missing model pull helper
- official docs/runbook access
- backend integration checklist view
- Social Agent / Facebook Graph safe config and manual gate UI
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.backend_health import build_health_summary  # noqa: E402
from shared.drive_paths import CONFIG_DIR, LOGS_DIR, WORKSTATION_LINKS_JSON  # noqa: E402
from shared.job_queue_schema import read_json, write_json  # noqa: E402
from shared.json_utils import update_workstation_status  # noqa: E402
from shared.model_health import MODEL_HEALTH_JSON, RECOMMENDED_MODELS, build_model_health, pull_missing_models  # noqa: E402
from social_agent.facebook_graph_backend import (  # noqa: E402
    APPROVED_JOBS_JSON,
    FACEBOOK_CONFIG_JSON,
    SOCIAL_POST_LOG_JSON,
    approved_items,
    ensure_config,
    gated_post_to_facebook,
)

PHASE = "2.19"
PHASE_STATUS = "model-health-social-agent-ready"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def render_model_health() -> None:
    st.header("Model Health / Missing Model Helper")
    if st.button("Refresh model health", type="primary"):
        status = build_model_health()
        st.success(f"Model health written to {MODEL_HEALTH_JSON}")
        st.json(status)
    else:
        status = read_json(MODEL_HEALTH_JSON, {}) if MODEL_HEALTH_JSON.exists() else build_model_health()
        st.json(status)
    st.download_button("Download model_health_status.json", data=json.dumps(status, ensure_ascii=False, indent=2), file_name="model_health_status.json", mime="application/json")
    st.markdown("### Missing model pull helper")
    options = list(RECOMMENDED_MODELS.values())
    selected = st.multiselect("Models to pull", options, default=[RECOMMENDED_MODELS["cpu_recommended"], RECOMMENDED_MODELS["cpu_emergency"]])
    if st.button("Pull selected missing models"):
        result = pull_missing_models(selected)
        st.json(result)


def render_backend_health() -> None:
    st.header("Backend Health Summary")
    summary = build_health_summary()
    st.json(summary)
    st.download_button("Download backend_health_summary.json", data=json.dumps(summary, ensure_ascii=False, indent=2), file_name="backend_health_summary.json", mime="application/json")


def render_social_agent_config() -> None:
    st.header("Social Agent / Facebook Graph Config")
    config = ensure_config()
    st.warning("Safe default: enabled=false and dry_run=true. No real Facebook post is sent unless you explicitly change config and manually confirm.")
    with st.form("facebook_config_form"):
        enabled = st.checkbox("Enable Facebook backend", value=bool(config.get("enabled", False)))
        dry_run = st.checkbox("Dry run only", value=bool(config.get("dry_run", True)))
        manual_required = st.checkbox("Manual approval required", value=bool(config.get("manual_approval_required", True)))
        page_id = st.text_input("Facebook page_id", value=str(config.get("page_id", "")))
        token_env = st.text_input("Access token environment variable", value=str(config.get("access_token_env", "FACEBOOK_PAGE_ACCESS_TOKEN")))
        version = st.text_input("Graph API version", value=str(config.get("graph_api_version", "v19.0")))
        submitted = st.form_submit_button("Save Facebook config")
    if submitted:
        new_config = {
            "enabled": enabled,
            "manual_approval_required": manual_required,
            "dry_run": dry_run,
            "page_id": page_id.strip(),
            "access_token_env": token_env.strip() or "FACEBOOK_PAGE_ACCESS_TOKEN",
            "graph_api_version": version.strip() or "v19.0",
            "notes": "Saved from Dashboard Phase 2.19. Keep dry_run=true until final manual API test.",
        }
        write_json(FACEBOOK_CONFIG_JSON, new_config)
        st.success(f"Config saved: {FACEBOOK_CONFIG_JSON}")
        st.json(new_config)
    st.markdown("### Current config path")
    st.code(str(FACEBOOK_CONFIG_JSON))


def render_social_agent_post_gate() -> None:
    st.header("Manual Posting Gate")
    items = approved_items()
    st.metric("Approved jobs", len(items))
    if not items:
        st.info("No approved jobs found. Approve jobs in Social Review first.")
        return
    rows = [{"Review ID": item.get("review_id", ""), "Job ID": item.get("job_id", ""), "Project": item.get("project", ""), "Topic": item.get("topic", ""), "Path": item.get("job_path", "")} for item in items]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = st.selectbox("Select approved item", [row["Review ID"] or row["Job ID"] for row in rows])
    manual_confirm = st.checkbox("I manually reviewed and approve this post attempt", value=False)
    st.caption("With dry_run=true this only logs a dry-run post. With dry_run=false, enabled=true, page_id, token env, and manual confirmation, it attempts Graph API posting.")
    if st.button("Run gated post attempt", type="primary"):
        result = gated_post_to_facebook(selected, manual_confirm=manual_confirm)
        st.json(result)
    log = read_json(SOCIAL_POST_LOG_JSON, {"items": []}) if SOCIAL_POST_LOG_JSON.exists() else {"items": []}
    st.markdown("### Social post log")
    st.json(log)


def render_docs_runbook() -> None:
    st.header("Runbook / Checklist")
    docs = {
        "Social Agent Facebook Graph Plan": REPO_ROOT / "docs" / "social_agent_facebook_graph_plan.md",
        "Items 11-20 ready marker": REPO_ROOT / "docs" / "backend_frontend_items_11_20_ready.md",
        "Phase 1.10 ready marker": REPO_ROOT / "docs" / "phase1_10_backend_frontend_ready.md",
        "README current marker": REPO_ROOT / "docs" / "README.md",
    }
    selected = st.selectbox("Open doc", list(docs.keys()))
    path = docs[selected]
    st.caption(str(path))
    st.text_area("Preview", read_text(path), height=520)


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": now_iso()})
    st.title("🧪 Naz Lab Master Dashboard")
    st.caption("Phase 2.19 — model health, missing model helper, social agent safe Facebook gate, runbook/checklist")
    tabs = st.tabs(["Model Health", "Backend Health", "Facebook Config", "Manual Post Gate", "Runbook"])
    with tabs[0]:
        render_model_health()
    with tabs[1]:
        render_backend_health()
    with tabs[2]:
        render_social_agent_config()
    with tabs[3]:
        render_social_agent_post_gate()
    with tabs[4]:
        render_docs_runbook()


if __name__ == "__main__":
    main()
