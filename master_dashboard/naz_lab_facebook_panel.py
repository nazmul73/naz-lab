"""Reusable Facebook Post / Social Gate panel for Naz Lab.

Supports multiple Facebook targets/pages/profiles/accounts in a safe manual-gated flow.
Real Facebook posting remains disabled/manual-gated by default.
"""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from final_package.package_backend import APPROVED_PACKAGES_JSON, list_packages, package_preview
from master_dashboard.naz_lab_nav import render_nav
from shared.job_queue_schema import read_json, write_json
from social_agent.facebook_graph_backend import (
    FACEBOOK_CONFIG_JSON,
    SOCIAL_POST_LOG_JSON,
    approved_items,
    bridge_latest_approved_packages,
    bridge_package_to_social_job,
    ensure_config,
    gated_post_to_facebook,
    save_multi_target_config,
    target_options,
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
    config = ensure_config()
    targets = target_options(config)
    log = read_json(SOCIAL_POST_LOG_JSON, {"items": []}) if SOCIAL_POST_LOG_JSON.exists() else {"items": []}
    log_items = log.get("items", []) if isinstance(log, dict) and isinstance(log.get("items"), list) else []
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Review packages", len(rows))
    c2.metric("Approved packages", len(approved_packages))
    c3.metric("Approved social jobs", len(social))
    c4.metric("Targets", len(targets))
    c5.metric("Social log entries", len(log_items))


def parse_targets_json(raw: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw)
    except Exception as exc:
        st.error(f"Invalid targets JSON: {exc}")
        return []
    if not isinstance(data, list):
        st.error("Targets JSON must be a list.")
        return []
    return [item for item in data if isinstance(item, dict)]


def target_label_map(targets: list[dict[str, Any]]) -> tuple[list[str], dict[str, str]]:
    labels = [f"{t.get('target_key')} | {t.get('label')} | {t.get('target_type')}" for t in targets]
    lookup = {label: str(targets[index].get("target_key")) for index, label in enumerate(labels)}
    return labels, lookup


def render_safe_config() -> None:
    st.markdown("### Multi-target Facebook config")
    config = ensure_config()
    targets = target_options(config)
    st.warning("Safe default: global enabled=false and dry_run=true. Add multiple pages/profiles here, but real posting stays blocked unless global config and target are explicitly enabled.")
    st.markdown("#### Current targets")
    st.dataframe(targets, use_container_width=True, hide_index=True)
    target_keys = [str(t.get("target_key", "")) for t in targets]
    with st.form("naz_lab_facebook_config_form"):
        enabled = st.checkbox("Enable Facebook backend globally", value=bool(config.get("enabled", False)))
        dry_run = st.checkbox("Dry run only", value=bool(config.get("dry_run", True)))
        manual_required = st.checkbox("Manual approval required", value=bool(config.get("manual_approval_required", True)))
        version = st.text_input("Graph API version", value=str(config.get("graph_api_version", "v19.0")))
        default_value = str(config.get("default_target_key", ""))
        default_index = target_keys.index(default_value) if default_value in target_keys else 0
        default_target = st.selectbox("Default target", target_keys or ["default_page"], index=default_index)
        targets_raw = st.text_area("Targets JSON", value=json.dumps(targets, ensure_ascii=False, indent=2), height=260, help="Add multiple pages/profiles. target_type may be page/profile/group/manual. Profiles are treated as manual handoff targets unless later supported.")
        notes = st.text_area("Notes", value=str(config.get("notes", "")), height=90)
        submitted = st.form_submit_button("Save multi-target config")
    if submitted:
        parsed_targets = parse_targets_json(targets_raw)
        if parsed_targets:
            new_config = save_multi_target_config(
                enabled=enabled,
                dry_run=dry_run,
                manual_approval_required=manual_required,
                graph_api_version=version.strip() or "v19.0",
                default_target_key=default_target,
                targets=parsed_targets,
                notes=notes,
            )
            st.success(f"Multi-target config saved: {FACEBOOK_CONFIG_JSON}")
            st.json(new_config)
    else:
        st.json(config)
    st.caption(str(FACEBOOK_CONFIG_JSON))


def render_package_handoff() -> None:
    st.markdown("### Approved package handoff")
    config = ensure_config()
    targets = target_options(config)
    labels, lookup = target_label_map(targets)
    selected_target_label = st.selectbox("Target page/profile", labels, key="facebook_handoff_target") if labels else ""
    selected_target_key = lookup.get(selected_target_label, "")

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
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Bridge selected package to selected target", type="primary", key="bridge_selected_package"):
            result = bridge_package_to_social_job(selected, note="bridged from Naz Lab Facebook Post tab", target_key=selected_target_key)
            st.json(result)
    with col_b:
        if st.button("Bridge latest approved packages to selected target", key="bridge_latest_packages"):
            result = bridge_latest_approved_packages(target_key=selected_target_key)
            st.json(result)
    st.caption("After bridging, open Manual Gate and run the safe gated attempt. With Facebook disabled, the expected result is a safe blocked-post log.")


def render_manual_gate() -> None:
    st.markdown("### Manual gated dry-run/post attempt")
    items = social_items()
    st.metric("Approved social jobs", len(items))
    if not items:
        st.info("No approved social jobs found. Bridge an approved package from the Approved Package tab first.")
        return
    rows = [
        {
            "Review ID": item.get("review_id", ""),
            "Job ID": item.get("job_id", ""),
            "Project": item.get("project", ""),
            "Topic": item.get("topic", ""),
            "Target": item.get("target_key", ""),
            "Target Label": item.get("target_label", ""),
            "Target Type": item.get("target_type", ""),
            "Package": item.get("package_id", ""),
        }
        for item in items
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = st.selectbox("Select approved social item", [row["Review ID"] or row["Job ID"] for row in rows], key="facebook_social_item_select")
    config = ensure_config()
    targets = target_options(config)
    labels, lookup = target_label_map(targets)
    target_choice = st.selectbox("Override target optional", ["Use job target"] + labels, key="facebook_manual_gate_target")
    target_key = None if target_choice == "Use job target" else lookup.get(target_choice)
    manual_confirm = st.checkbox("I manually reviewed and approve this post attempt", value=False, key="facebook_manual_confirm")
    st.caption("With dry_run=true this only logs a dry-run post. With enabled=false it should be blocked safely.")
    if st.button("Run gated post attempt", type="primary", key="facebook_run_gated_attempt"):
        result = gated_post_to_facebook(selected, manual_confirm=manual_confirm, target_key=target_key)
        st.json(result)


def render_social_log() -> None:
    st.markdown("### Social post log")
    log = read_json(SOCIAL_POST_LOG_JSON, {"items": []}) if SOCIAL_POST_LOG_JSON.exists() else {"items": []}
    st.json(log)
    st.download_button("Download social_post_log.json", data=json.dumps(log, ensure_ascii=False, indent=2), file_name="social_post_log.json", mime="application/json", key="download_social_log")


def render_facebook_panel() -> None:
    st.subheader("Facebook Post / Social Gate")
    st.write("Prepare Facebook-ready content, manage multiple pages/profiles, bridge approved packages to selected targets, and run safe manual-gated dry-run/post attempts from Naz Lab. Real posting remains disabled/manual-gated by default.")
    render_summary()
    selected = render_nav(["Approved Package", "Targets / Safe Config", "Manual Gate", "Social Log"], key="facebook_sub", variant="sub")
    if selected == "Approved Package":
        render_package_handoff()
    elif selected == "Targets / Safe Config":
        render_safe_config()
    elif selected == "Manual Gate":
        render_manual_gate()
    elif selected == "Social Log":
        render_social_log()
