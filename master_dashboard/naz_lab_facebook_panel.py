"""Reusable Facebook Post / Social Gate panel for Naz Lab.

This panel brings the safe Facebook dry-run/manual gate controls into the main
Naz Lab dashboard. Real Facebook posting remains disabled/manual-gated by
default.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from final_package.package_backend import APPROVED_PACKAGES_JSON, list_packages, package_preview
from shared.job_queue_schema import read_json, write_json
from social_agent.facebook_graph_backend import (
    APPROVED_JOBS_JSON,
    FACEBOOK_CONFIG_JSON,
    SOCIAL_POST_LOG_JSON,
    approved_items,
    ensure_config,
    gated_post_to_facebook,
)


def package_rows() -> list[dict[str, Any]]:
    return list_packages()


def approved_package_items() -> list[dict[str, Any]]:
    data = read_json(APPROVED_PACKAGES_JSON, {"items": []}) if APPROVED_PACKAGES_JSON.exists() else {"items": []}
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return [item for item in data["items"] if isinstance(item, dict)]
    return []


def social_items() -> list[dict[str, Any]]:
    return approved_items()


def render_summary() -> None:
    rows = package_rows()
    approved_packages = approved_package_items()
    social = social_items()
    log = read_json(SOCIAL_POST_LOG_JSON, {"items": []}) if SOCIAL_POST_LOG_JSON.exists() else {"items": []}
    log_items = log.get("items", []) if isinstance(log, dict) and isinstance(log.get("items"), list) else []
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Review packages", len(rows))
    c2.metric("Approved packages", len(approved_packages))
    c3.metric("Approved social jobs", len(social))
    c4.metric("Social log entries", len(log_items))


def render_safe_config() -> None:
    st.markdown("### Safe Facebook config")
    config = ensure_config()
    st.warning("Safe default: enabled=false and dry_run=true. No real Facebook post is sent unless config is explicitly changed and manually confirmed.")
    with st.form("naz_lab_facebook_config_form"):
        enabled = st.checkbox("Enable Facebook backend", value=bool(config.get("enabled", False)))
        dry_run = st.checkbox("Dry run only", value=bool(config.get("dry_run", True)))
        manual_required = st.checkbox("Manual approval required", value=bool(config.get("manual_approval_required", True)))
        page_id = st.text_input("Facebook page_id", value=str(config.get("page_id", "")))
        token_env = st.text_input("Access token environment variable", value=str(config.get("access_token_env", "FACEBOOK_PAGE_ACCESS_TOKEN")))
        version = st.text_input("Graph API version", value=str(config.get("graph_api_version", "v19.0")))
        submitted = st.form_submit_button("Save safe config")
    if submitted:
        new_config = {
            "enabled": enabled,
            "manual_approval_required": manual_required,
            "dry_run": dry_run,
            "page_id": page_id.strip(),
            "access_token_env": token_env.strip() or "FACEBOOK_PAGE_ACCESS_TOKEN",
            "graph_api_version": version.strip() or "v19.0",
            "notes": "Saved from Naz Lab Facebook Post tab. Keep dry_run=true until final manual API test.",
        }
        write_json(FACEBOOK_CONFIG_JSON, new_config)
        st.success(f"Config saved: {FACEBOOK_CONFIG_JSON}")
        st.json(new_config)
    else:
        st.json(config)
    st.caption(str(FACEBOOK_CONFIG_JSON))


def render_package_handoff() -> None:
    st.markdown("### Approved package handoff")
    approved_packages = approved_package_items()
    if not approved_packages:
        st.info("No approved review packages found yet. Approve a package from Home > Review Package Workflow first.")
        return
    st.dataframe(approved_packages, use_container_width=True, hide_index=True)
    package_path_options = [str(item.get("package_path", "")) for item in approved_packages if item.get("package_path")]
    if not package_path_options:
        st.warning("Approved package index exists, but package_path values are missing.")
        return
    selected = st.selectbox("Select approved package", package_path_options, key="facebook_package_handoff_select")
    preview = package_preview(selected)
    record = preview.get("record", {}) if isinstance(preview, dict) else {}
    st.markdown("#### Facebook-ready preview source")
    st.json(record)
    caption = str(record.get("caption_text", "") or record.get("topic", "") or "") if isinstance(record, dict) else ""
    prompt = str(record.get("manual_prompt", "")) if isinstance(record, dict) else ""
    message_preview = f"{caption}\n\n{prompt}".strip()
    st.text_area("Draft post text preview", value=message_preview, height=220, key="facebook_package_message_preview")
    st.caption("This is a preview source. The current social backend posts from approved social jobs; package-to-social-job bridge is the next polish step.")


def render_manual_gate() -> None:
    st.markdown("### Manual gated dry-run/post attempt")
    items = social_items()
    st.metric("Approved social jobs", len(items))
    if not items:
        st.info("No approved social jobs found. Package-to-social-job bridge will be added next; for now, this confirms the safe gate state.")
        return
    rows = [
        {
            "Review ID": item.get("review_id", ""),
            "Job ID": item.get("job_id", ""),
            "Project": item.get("project", ""),
            "Topic": item.get("topic", ""),
            "Path": item.get("job_path", ""),
        }
        for item in items
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = st.selectbox("Select approved social item", [row["Review ID"] or row["Job ID"] for row in rows], key="facebook_social_item_select")
    manual_confirm = st.checkbox("I manually reviewed and approve this post attempt", value=False, key="facebook_manual_confirm")
    st.caption("With dry_run=true this only logs a dry-run post. With enabled=false it should be blocked safely.")
    if st.button("Run gated post attempt", type="primary", key="facebook_run_gated_attempt"):
        result = gated_post_to_facebook(selected, manual_confirm=manual_confirm)
        st.json(result)


def render_social_log() -> None:
    st.markdown("### Social post log")
    log = read_json(SOCIAL_POST_LOG_JSON, {"items": []}) if SOCIAL_POST_LOG_JSON.exists() else {"items": []}
    st.json(log)
    st.download_button("Download social_post_log.json", data=str(log), file_name="social_post_log.json", mime="application/json", key="download_social_log")


def render_facebook_panel() -> None:
    st.subheader("Facebook Post / Social Gate")
    st.write("Prepare Facebook-ready content, inspect approved packages, and run safe manual-gated dry-run/post attempts from Naz Lab. Real posting remains disabled/manual-gated by default.")
    render_summary()
    tabs = st.tabs(["Approved Package", "Safe Config", "Manual Gate", "Social Log"])
    with tabs[0]:
        render_package_handoff()
    with tabs[1]:
        render_safe_config()
    with tabs[2]:
        render_manual_gate()
    with tabs[3]:
        render_social_log()
