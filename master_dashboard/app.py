"""Naz Lab Master Control Dashboard Phase 2.16.1 package search hotfix.

This dashboard is intentionally lightweight. It scans saved Naz Lab JSON packages
from Google Drive, previews them, and exports search reports. Real video
generation remains deferred after v1.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.backend_queue import scan_backend_queues  # noqa: E402
from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    CHAT_OUTPUTS,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    IMAGE_PROMPTS,
    OUTPUT_LOG_JSON,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    VIDEO_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import safe_read_json, update_workstation_status  # noqa: E402

PHASE = "2.16.1"
PHASE_STATUS = "stable-deep-package-search-hotfix"

VOICE_OUTPUTS = BASE_PATH / "voice_outputs"
VOICE_PACKAGES = BASE_PATH / "voice_packages"
VOICE_PROFILE_PACKAGES = BASE_PATH / "voice_profile_packages"
AUDIO_OUTPUTS = BASE_PATH / "audio_outputs"
VIDEO_PACKAGES = BASE_PATH / "video_packages"
VIDEO_STORYBOARDS = BASE_PATH / "video_storyboards"
PORTRAIT_PACKAGES = BASE_PATH / "portrait_packages"
PORTRAIT_OUTPUTS = BASE_PATH / "portrait_outputs"
PROJECT_PACKAGES = BASE_PATH / "project_packages"
PROJECT_WORKFLOWS = BASE_PATH / "project_workflows"
FINAL_REEL_PACKS = BASE_PATH / "final_reel_packs"
TEST_CONSOLE_PACKAGES = BASE_PATH / "test_console_packages"

LANGUAGE_REQUIREMENT_BN = "Naz Lab default হবে Bangla-first। English থাকবে selected English project বা user request অনুযায়ী।"
LANGUAGE_REQUIREMENT_EN = "Naz Lab is Bangla-first by default. English remains available for selected projects such as True Noir Tales and ToolFlow."
VIDEO_DEFERRED = "Real video generation is deferred after v1. This dashboard only previews saved plans/manifests/packages."

PROJECT_AUTOMATION_STATUS = {
    "General Bangla": "real content package trial passed",
    "True Noir Tales": "real content package trial passed",
    "ToolFlow": "saved; dashboard verification pending",
    "Input Test Console": "frontend practical testing layer passed",
}

FOLDERS = {
    "Chat outputs": CHAT_OUTPUTS,
    "Text outputs": TEXT_OUTPUTS,
    "Script outputs": SCRIPT_OUTPUTS,
    "Image prompts": IMAGE_PROMPTS,
    "Image jobs": IMAGE_JOBS,
    "Image outputs": IMAGE_OUTPUTS,
    "Voice outputs": VOICE_OUTPUTS,
    "Voice packages": VOICE_PACKAGES,
    "Voice profile packages": VOICE_PROFILE_PACKAGES,
    "Audio outputs": AUDIO_OUTPUTS,
    "Video outputs": VIDEO_OUTPUTS,
    "Video packages": VIDEO_PACKAGES,
    "Video storyboards": VIDEO_STORYBOARDS,
    "Portrait packages": PORTRAIT_PACKAGES,
    "Portrait outputs": PORTRAIT_OUTPUTS,
    "Project packages": PROJECT_PACKAGES,
    "Project workflows": PROJECT_WORKFLOWS,
    "Final reel packs": FINAL_REEL_PACKS,
    "Test console packages": TEST_CONSOLE_PACKAGES,
}

PACKAGE_FOLDERS = {
    "Project packages": PROJECT_PACKAGES,
    "Image jobs": IMAGE_JOBS,
    "Voice packages": VOICE_PACKAGES,
    "Voice profile packages": VOICE_PROFILE_PACKAGES,
    "Video packages": VIDEO_PACKAGES,
    "Portrait packages": PORTRAIT_PACKAGES,
    "Final reel packs": FINAL_REEL_PACKS,
    "Test console packages": TEST_CONSOLE_PACKAGES,
}

WORKSTATIONS = [
    {"name": "Input Test Console", "phase": "1.2 stable", "key": "test_console", "folder": TEST_CONSOLE_PACKAGES, "port": "8508"},
    {"name": "Text Workstation", "phase": "1.8 stable", "key": "text_workstation", "folder": TEXT_OUTPUTS, "port": "8501"},
    {"name": "Master Dashboard", "phase": "2.16.1 hotfix", "key": "master_dashboard", "folder": BASE_PATH, "port": "8502"},
    {"name": "Image Workstation", "phase": "3.x stable", "key": "image_workstation", "folder": IMAGE_OUTPUTS, "port": "8503"},
    {"name": "Voice Workstation", "phase": "4.5 safe reference manager", "key": "voice_workstation", "folder": VOICE_OUTPUTS, "port": "8504"},
    {"name": "Video Workstation", "phase": "5.3 planning only", "key": "video_workstation", "folder": VIDEO_OUTPUTS, "port": "8505"},
    {"name": "Portrait Workstation", "phase": "6.4 safe reference manager", "key": "portrait_workstation", "folder": PORTRAIT_PACKAGES, "port": "8506"},
    {"name": "Project Workflow Workstation", "phase": "10.3 stable", "key": "project_workstation", "folder": PROJECT_PACKAGES, "port": "8507"},
]


def read_json(path: Path, default: Any) -> Any:
    try:
        return safe_read_json(path, default)
    except Exception:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default


def safe_json_text(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        return str(data)


def normalize_text(value: Any) -> str:
    return str(value).replace("_", " ").replace("-", " ").lower()


def deep_text(value: Any) -> str:
    """Flatten nested JSON into searchable text including keys and values."""
    if isinstance(value, dict):
        return " ".join(f"{key} {deep_text(val)}" for key, val in value.items())
    if isinstance(value, list):
        return " ".join(deep_text(item) for item in value)
    return str(value)


def count_files(folder: Path, pattern: str = "*") -> int:
    if not folder.exists():
        return 0
    return sum(1 for item in folder.rglob(pattern) if item.is_file())


def latest_files(folder: Path, limit: int = 10, pattern: str = "*") -> list[Path]:
    if not folder.exists():
        return []
    files = [item for item in folder.rglob(pattern) if item.is_file()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def status_label(folder: Path) -> str:
    return "OK" if folder.exists() and folder.is_dir() else "Missing"


def workstation_data() -> dict[str, Any]:
    data = read_json(WORKSTATION_LINKS_JSON, {})
    return data if isinstance(data, dict) else {}


def output_log_entries() -> list[dict[str, Any]]:
    data = read_json(OUTPUT_LOG_JSON, {"logs": []})
    if isinstance(data, dict) and isinstance(data.get("logs"), list):
        return data["logs"]
    if isinstance(data, list):
        return data
    return []


def package_summary(path: Path) -> dict[str, Any]:
    data = read_json(path, {})
    text_blob = deep_text(data) if isinstance(data, (dict, list)) else ""
    project = topic = status = platform = created = workflow = ""
    if isinstance(data, dict):
        project = str(data.get("project", data.get("project_preset", data.get("visual_preset", ""))))
        topic = str(data.get("topic", data.get("prompt", data.get("title", ""))))
        status = str(data.get("backend_status", data.get("status", "unknown")))
        platform = str(data.get("platform", data.get("content_type", data.get("portrait_type", ""))))
        created = str(data.get("created_at", ""))
        workflow = str(data.get("workflow", data.get("phase", "")))
    raw_search = f"{path.name} {path.parent.name} {path} {project} {workflow} {status} {platform} {topic} {text_blob}"
    return {
        "File": path.name,
        "Folder": path.parent.name,
        "Project": project,
        "Workflow": workflow,
        "Status": status or "unknown",
        "Platform": platform,
        "Topic": topic[:180],
        "Created": created,
        "Modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "Path": str(path),
        "SearchText": raw_search,
        "SearchTextNormalized": normalize_text(raw_search),
    }


def load_package_rows(folder: Path, limit: int, recursive: bool = True) -> list[dict[str, Any]]:
    pattern = "*.json"
    files = latest_files(folder, limit=limit, pattern=pattern) if recursive else [item for item in folder.glob(pattern) if item.is_file()]
    return [package_summary(path) for path in files]


def display_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hidden = {"SearchText", "SearchTextNormalized"}
    return [{k: v for k, v in row.items() if k not in hidden} for row in rows]


def rows_to_csv(rows: list[dict[str, Any]]) -> str:
    clean = display_rows(rows)
    if not clean:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(clean[0].keys()))
    writer.writeheader()
    writer.writerows(clean)
    return output.getvalue()


def rows_to_markdown(rows: list[dict[str, Any]]) -> str:
    lines = ["# Naz Lab Package Search Report", "", f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    for index, row in enumerate(display_rows(rows), start=1):
        lines.extend([
            f"## {index}. {row.get('File', '')}",
            f"- Folder: {row.get('Folder', '')}",
            f"- Project: {row.get('Project', '')}",
            f"- Workflow: {row.get('Workflow', '')}",
            f"- Status: {row.get('Status', '')}",
            f"- Platform: {row.get('Platform', '')}",
            f"- Topic: {row.get('Topic', '')}",
            f"- Created: {row.get('Created', '')}",
            f"- Modified: {row.get('Modified', '')}",
            f"- Path: `{row.get('Path', '')}`",
            "",
        ])
    return "\n".join(lines)


def package_to_markdown(path: Path, data: Any) -> str:
    lines = [f"# Naz Lab Package Export: {path.name}", "", f"Exported: {datetime.now().isoformat(timespec='seconds')}", f"Source path: `{path}`", ""]
    if isinstance(data, dict):
        priority_keys = ["project", "project_preset", "workflow", "topic", "title", "status", "backend_status", "platform", "content_type", "language", "audience", "direction", "created_at"]
        lines.append("## Summary")
        for key in priority_keys:
            if key in data:
                lines.append(f"- {key}: {data.get(key)}")
        lines.extend(["", "## Full JSON", "", "```json", safe_json_text(data), "```"])
    else:
        lines.extend(["## Content", "", str(data)])
    return "\n".join(lines)


def keyword_match(row: dict[str, Any], keyword: str, mode: str) -> bool:
    if not keyword:
        return True
    raw = str(row.get("SearchText", "")).lower()
    normalized = str(row.get("SearchTextNormalized", ""))
    keyword_raw = keyword.lower().strip()
    keyword_norm = normalize_text(keyword_raw)
    if mode == "Exact phrase":
        return keyword_raw in raw or keyword_norm in normalized
    tokens = [token for token in keyword_norm.split() if token]
    return all(token in normalized for token in tokens)


def collect_package_rows(folder_label: str, limit: int) -> list[dict[str, Any]]:
    folders = PACKAGE_FOLDERS.values() if folder_label == "All package folders" else [PACKAGE_FOLDERS[folder_label]]
    rows: list[dict[str, Any]] = []
    for folder in folders:
        rows.extend(load_package_rows(folder, int(limit), recursive=True))
    return sorted(rows, key=lambda item: item.get("Modified", ""), reverse=True)


def flatten_backend_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group, group_rows in report.get("folders", {}).items():
        for row in group_rows:
            rows.append({
                "Group": group,
                "Kind": row.get("kind", ""),
                "File": row.get("file", ""),
                "Project": row.get("project", ""),
                "Package status": row.get("status", ""),
                "Validation": row.get("validation_status", ""),
                "Ready": row.get("ok", False),
                "Messages": "; ".join(str(item) for item in row.get("messages", [])),
                "Warnings": "; ".join(str(item) for item in row.get("warnings", [])),
                "Modified": row.get("modified", ""),
                "Path": row.get("path", ""),
            })
    return sorted(rows, key=lambda item: item.get("Modified", ""), reverse=True)


def render_status(language: str) -> None:
    st.header("System status")
    links = workstation_data()
    logs = output_log_entries()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Dashboard phase", PHASE)
    c2.metric("Status", PHASE_STATUS)
    c3.metric("Drive base", status_label(BASE_PATH))
    c4.metric("Workstations", str(len(WORKSTATIONS)))
    c5.metric("Output log entries", len(logs))
    st.success("Master Dashboard status: package-search hotfix ready")
    st.info(LANGUAGE_REQUIREMENT_BN if language == "Bangla" else LANGUAGE_REQUIREMENT_EN)
    st.warning(VIDEO_DEFERRED)
    rows = []
    for item in WORKSTATIONS:
        data = links.get(item["key"], {})
        rows.append({
            "Workstation": item["name"],
            "Phase": item["phase"],
            "Saved status": data.get("status", "planned"),
            "Folder": status_label(item["folder"]),
            "Files": count_files(item["folder"]),
            "Port": item["port"],
            "URL saved": "yes" if data.get("public_url") else "no",
            "Last seen": data.get("last_seen", ""),
        })
    st.markdown("### Workstation matrix")
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.markdown("### Project automation status")
    st.json(PROJECT_AUTOMATION_STATUS)


def render_links() -> None:
    st.header("Links")
    links = workstation_data()
    with st.form("save_links_form"):
        values = {}
        for item in WORKSTATIONS:
            data = links.get(item["key"], {})
            values[item["key"]] = st.text_input(f"{item['name']} public/proxy URL", value=data.get("public_url", ""))
        submitted = st.form_submit_button("Save URLs")
    if submitted:
        for item in WORKSTATIONS:
            url = values[item["key"]].strip()
            if url:
                update_workstation_status(WORKSTATION_LINKS_JSON, item["key"], {"public_url": url, "status": "stable", "phase": item["phase"]})
        st.success("URLs saved to workstation_links.json")
        st.rerun()


def render_workstations() -> None:
    st.header("Workstations")
    links = workstation_data()
    rows = []
    for item in WORKSTATIONS:
        data = links.get(item["key"], {})
        rows.append({"Workstation": item["name"], "Phase": item["phase"], "Status": data.get("status", "planned"), "Folder status": status_label(item["folder"]), "Files": count_files(item["folder"]), "Public URL": data.get("public_url", ""), "Last updated": data.get("last_updated", data.get("last_seen", ""))})
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_outputs() -> None:
    st.header("Output folders")
    cols = st.columns(4)
    for index, (label, folder) in enumerate(FOLDERS.items()):
        with cols[index % 4]:
            st.metric(label, count_files(folder))
            st.caption(str(folder))
    st.markdown("### Latest files")
    for label, folder in FOLDERS.items():
        with st.expander(label, expanded=False):
            files = latest_files(folder, limit=5)
            if not files:
                st.info("No files yet.")
            for path in files:
                modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(f"**{path.name}** — {modified}")


def render_jobs() -> None:
    st.header("Job queue")
    for label, folder in PACKAGE_FOLDERS.items():
        st.markdown(f"### {label}")
        rows = load_package_rows(folder, 30)
        st.metric(f"{label} count", len(rows))
        if rows:
            st.dataframe(display_rows(rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"No {label.lower()} yet.")


def render_backend_status() -> None:
    st.header("Backend status")
    st.caption("Lightweight backend readiness scan. Heavy generation tools are not run here.")
    report = scan_backend_queues(limit_per_folder=100)
    summary = report.get("summary", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total packages", summary.get("total", 0))
    c2.metric("Ready", summary.get("ready", 0))
    c3.metric("Blocked", summary.get("blocked", 0))
    c4.metric("Warning only", summary.get("warning_only", 0))
    rows = flatten_backend_rows(report)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No backend package/job JSON files found yet.")
    st.download_button("Download backend scan JSON", data=safe_json_text(report), file_name="naz_lab_backend_scan_report.json", mime="application/json")


def render_final_packs() -> None:
    st.header("Final reel packs")
    st.caption("Preview and download final reel pack JSON/Markdown manifests. This tab does not render final video.")
    FINAL_REEL_PACKS.mkdir(parents=True, exist_ok=True)
    json_files = latest_files(FINAL_REEL_PACKS, limit=500, pattern="*.json")
    md_files = {path.stem: path for path in latest_files(FINAL_REEL_PACKS, limit=500, pattern="*.md")}
    st.metric("Final pack JSON files", len(json_files))
    st.metric("Final pack Markdown files", len(md_files))
    if not json_files:
        st.info("No final reel packs found yet.")
        return
    rows = [package_summary(path) for path in json_files]
    st.dataframe(display_rows(rows), use_container_width=True, hide_index=True)
    selected_path = st.selectbox("Open final reel pack", [str(path) for path in json_files])
    selected = Path(selected_path)
    data = read_json(selected, {})
    json_text = safe_json_text(data)
    markdown_path = md_files.get(selected.stem)
    markdown_text = markdown_path.read_text(encoding="utf-8", errors="ignore") if markdown_path and markdown_path.exists() else package_to_markdown(selected, data)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download final pack JSON", data=json_text, file_name=selected.name, mime="application/json")
    with c2:
        st.download_button("Download final pack Markdown", data=markdown_text, file_name=f"{selected.stem}.md", mime="text/markdown")
    st.markdown("### Pack preview")
    st.json(data)
    st.text_area("Copy final pack JSON", json_text, height=360)
    st.text_area("Copy final pack Markdown", markdown_text, height=300)


def render_toolflow_verification() -> None:
    st.markdown("### ToolFlow verification helper")
    st.caption("This helper does not mark PASS. It only shows whether the required Dashboard search keywords are discoverable.")
    required = ["ToolFlow", "under 30 minutes", "small business owners", "frontend_full_package_toolflow"]
    rows = collect_package_rows("All package folders", 1000)
    report = []
    for keyword in required:
        matches = [row for row in rows if keyword_match(row, keyword, "Token match")]
        report.append({"Keyword": keyword, "Found": bool(matches), "Matches": len(matches), "Latest match": matches[0]["File"] if matches else ""})
    st.dataframe(report, use_container_width=True, hide_index=True)
    all_found = all(item["Found"] for item in report)
    if all_found:
        st.success("ToolFlow search keywords are all discoverable. User preview/download/export confirmation is still required before PASS marker.")
    else:
        st.warning("One or more ToolFlow verification keywords are missing from searchable saved package content. Do not mark ToolFlow PASS yet.")


def render_package_search() -> None:
    st.header("Package search")
    st.caption("Hotfix: recursive JSON scan, filename/path/project/workflow/full nested JSON content search, and token matching for identifiers.")
    c1, c2, c3, c4 = st.columns(4)
    folder_label = c1.selectbox("Folder", ["All package folders"] + list(PACKAGE_FOLDERS.keys()))
    project_filter = c2.text_input("Project contains", value="")
    status_filter = c3.text_input("Status contains", value="")
    limit = c4.number_input("Latest files per folder", min_value=5, max_value=2000, value=500, step=25)
    keyword = st.text_input("Keyword anywhere in package JSON/file/path", value="")
    match_mode = st.radio("Match mode", ["Token match", "Exact phrase"], index=0, horizontal=True)
    rows = collect_package_rows(folder_label, int(limit))

    def keep(row: dict[str, Any]) -> bool:
        normalized = str(row.get("SearchTextNormalized", ""))
        if project_filter and normalize_text(project_filter) not in normalized:
            return False
        if status_filter and normalize_text(status_filter) not in normalize_text(row.get("Status", "")):
            return False
        if not keyword_match(row, keyword, match_mode):
            return False
        return True

    rows = [row for row in rows if keep(row)]
    st.metric("Matching packages", len(rows))
    if not rows:
        st.info("No matching packages found. Try All package folders, Token match, and increasing latest files per folder.")
        render_toolflow_verification()
        return
    visible_rows = display_rows(rows)
    st.dataframe(visible_rows, use_container_width=True, hide_index=True)
    report_payload = {"generated_at": datetime.now().isoformat(timespec="seconds"), "phase": PHASE, "filters": {"folder": folder_label, "project": project_filter, "status": status_filter, "keyword": keyword, "match_mode": match_mode}, "matches": visible_rows}
    report_json = safe_json_text(report_payload)
    export_cols = st.columns(3)
    with export_cols[0]:
        st.download_button("Download report JSON", data=report_json, file_name="naz_lab_package_search_report.json", mime="application/json")
    with export_cols[1]:
        st.download_button("Download report CSV", data=rows_to_csv(rows), file_name="naz_lab_package_search_report.csv", mime="text/csv")
    with export_cols[2]:
        st.download_button("Download report Markdown", data=rows_to_markdown(rows), file_name="naz_lab_package_search_report.md", mime="text/markdown")
    selected_path = st.selectbox("Open package JSON", [row["Path"] for row in rows])
    selected = Path(selected_path)
    data = read_json(selected, {})
    package_json = safe_json_text(data)
    package_md = package_to_markdown(selected, data)
    package_txt = f"Naz Lab Package Export\nSource: {selected}\nExported: {datetime.now().isoformat(timespec='seconds')}\n\n{package_json}"
    st.markdown(f"### Preview: `{selected.name}`")
    selected_cols = st.columns(3)
    with selected_cols[0]:
        st.download_button("Download selected JSON", data=package_json, file_name=selected.name, mime="application/json")
    with selected_cols[1]:
        st.download_button("Download selected TXT", data=package_txt, file_name=f"{selected.stem}.txt", mime="text/plain")
    with selected_cols[2]:
        st.download_button("Download selected Markdown", data=package_md, file_name=f"{selected.stem}.md", mime="text/markdown")
    st.json(data)
    st.text_area("Copy package JSON", package_json, height=420)
    st.text_area("Copy package Markdown", package_md, height=260)
    render_toolflow_verification()


def render_launch() -> None:
    st.header("Launch instructions")
    st.write({"Input Test Console": "8508", "Master Dashboard": "8502"})
    st.code("python -m streamlit run master_dashboard/app.py --server.port 8502 --server.address 0.0.0.0", language="bash")


def render_roadmap(language: str) -> None:
    st.header("Roadmap")
    st.markdown("""
1. Phase 0 Foundation — complete  
2. Phase 1 Text Workstation — stable  
3. Phase 2 Master Dashboard — stable with package search hotfix  
4. Phase 3 Image Workstation — stable  
5. Phase 4 Voice Workstation — safer reference manager active  
6. Phase 5 Video Workstation — stable planning/manifest only  
7. Phase 6 Portrait Workstation — safer reference manager active  
8. Input Test Console practical frontend testing — passed  
9. Real content package trials — pending ToolFlow Dashboard verification
""")
    st.markdown("### v1.5 options after trials complete")
    st.write(["real image backend", "FFmpeg assembly", "real video generation groundwork", "higher quality TTS", "local PC deployment support"])
    if language == "Bangla":
        st.info("ToolFlow verification done না হওয়া পর্যন্ত PASS marker বা trials COMPLETE marker দেওয়া যাবে না।")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Control Dashboard")
    st.caption("Phase 2.16.1 — package search hotfix, recursive deep JSON search, backend status, and final pack preview/download")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    with st.sidebar:
        st.header("Dashboard settings")
        language = st.radio("Dashboard language note", ["Bangla", "English"], index=0)
        st.caption("Naz Lab default: Bangla-first.")
        st.success("Phase 2.16.1 hotfix")
    tabs = st.tabs(["Status", "Links", "Workstations", "Outputs", "Job Queue", "Backend Status", "Final Packs", "Package Search", "Launch", "Roadmap"])
    with tabs[0]:
        render_status(language)
    with tabs[1]:
        render_links()
    with tabs[2]:
        render_workstations()
    with tabs[3]:
        render_outputs()
    with tabs[4]:
        render_jobs()
    with tabs[5]:
        render_backend_status()
    with tabs[6]:
        render_final_packs()
    with tabs[7]:
        render_package_search()
    with tabs[8]:
        render_launch()
    with tabs[9]:
        render_roadmap(language)


if __name__ == "__main__":
    main()
