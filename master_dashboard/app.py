"""Naz Lab Master Control Dashboard Phase 2.16 deep package search."""

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

PHASE = "2.16"
PHASE_STATUS = "stable-deep-package-search"

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

LANGUAGE_REQUIREMENT_BN = "Naz Lab default হবে Bangla-first। বেশির ভাগ কনটেন্ট বাংলায় হবে। English থাকবে selected English project বা user request অনুযায়ী। আঞ্চলিক বাংলা লাগলে primary default: রংপুর/নীলফামারী/উত্তরবঙ্গ।"
LANGUAGE_REQUIREMENT_EN = "Naz Lab is Bangla-first by default. English remains available for selected projects such as True Noir Tales and ToolFlow."

BANGLA_STYLE_REQUIREMENTS = {
    "Core Bangla": "স্বাভাবিক, সহজ, মুখে বলার মতো, ready-to-use বাংলা।",
    "Voiceover Bangla": "short sentence, clear pacing, not stiff textbook Bangla.",
    "Primary regional Bangla": "Rangpur/Nilphamari/North Bengal flavor when useful.",
}

PROJECT_AUTOMATION_STATUS = {
    "General Bangla": "real content package trial passed",
    "True Noir Tales": "real content package trial in progress",
    "ToolFlow": "real content package trial pending",
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
    {"name": "Master Dashboard", "phase": "2.16 stable", "key": "master_dashboard", "folder": BASE_PATH, "port": "8502"},
    {"name": "Image Workstation", "phase": "3.x stable", "key": "image_workstation", "folder": IMAGE_OUTPUTS, "port": "8503"},
    {"name": "Voice Workstation", "phase": "4.5 safe reference manager", "key": "voice_workstation", "folder": VOICE_OUTPUTS, "port": "8504"},
    {"name": "Video Workstation", "phase": "5.3 stable", "key": "video_workstation", "folder": VIDEO_OUTPUTS, "port": "8505"},
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


def deep_text(value: Any) -> str:
    """Flatten nested package JSON into searchable text."""
    if isinstance(value, dict):
        return " ".join([str(k) + " " + deep_text(v) for k, v in value.items()])
    if isinstance(value, list):
        return " ".join(deep_text(v) for v in value)
    return str(value)


def count_files(folder: Path, pattern: str = "*") -> int:
    if not folder.exists():
        return 0
    return sum(1 for item in folder.glob(pattern) if item.is_file())


def latest_files(folder: Path, limit: int = 10, pattern: str = "*") -> list[Path]:
    if not folder.exists():
        return []
    files = [item for item in folder.glob(pattern) if item.is_file()]
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
    project = ""
    topic = ""
    status = "unknown"
    platform = ""
    created = ""
    if isinstance(data, dict):
        project = str(data.get("project", data.get("project_preset", data.get("visual_preset", ""))))
        topic = str(data.get("topic", data.get("prompt", data.get("title", ""))))
        status = str(data.get("backend_status", data.get("status", "unknown")))
        platform = str(data.get("platform", data.get("content_type", data.get("portrait_type", ""))))
        created = str(data.get("created_at", ""))
    return {
        "File": path.name,
        "Folder": path.parent.name,
        "Project": project,
        "Status": status,
        "Platform": platform,
        "Topic": topic[:140],
        "Created": created,
        "Modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "Path": str(path),
        "SearchText": f"{path.name} {path.parent.name} {path} {project} {status} {platform} {topic} {text_blob}",
    }


def load_package_rows(folder: Path, limit: int) -> list[dict[str, Any]]:
    return [package_summary(path) for path in latest_files(folder, limit=limit, pattern="*.json")]


def display_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: v for k, v in row.items() if k != "SearchText"} for row in rows]


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
        priority_keys = ["project", "project_preset", "workflow", "topic", "title", "status", "backend_status", "platform", "content_type", "language", "created_at"]
        lines.append("## Summary")
        for key in priority_keys:
            if key in data:
                lines.append(f"- {key}: {data.get(key)}")
        lines.extend(["", "## Full JSON", "", "```json", safe_json_text(data), "```"])
    else:
        lines.extend(["## Content", "", str(data)])
    return "\n".join(lines)


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
    c2.metric("Dashboard status", PHASE_STATUS)
    c3.metric("Drive base", status_label(BASE_PATH))
    c4.metric("Active workstations", str(len(WORKSTATIONS)))
    c5.metric("Output log entries", len(logs))
    st.success("Master Dashboard status: stable for Phase 2.16 with deep package search")
    st.info(LANGUAGE_REQUIREMENT_BN if language == "Bangla" else LANGUAGE_REQUIREMENT_EN)
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
    st.markdown("### Current readiness")
    st.write({
        "current_stack": "Input Test Console + Dashboard + Text/Image/Voice/Video planning/Portrait + Project Workflow",
        "package_search": "deep search across full nested JSON content",
        "video_generation": "deferred after v1",
        "status": "ready",
    })
    st.markdown("### Bangla-first quality requirements")
    st.json(BANGLA_STYLE_REQUIREMENTS)


def render_links() -> None:
    st.header("Links")
    st.caption("Save current Cloudflare or Colab proxy URLs so the dashboard can show quick open links.")
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
    sections = {"Image jobs": IMAGE_JOBS, "Voice packages": VOICE_PACKAGES, "Voice profile packages": VOICE_PROFILE_PACKAGES, "Video packages": VIDEO_PACKAGES, "Portrait packages": PORTRAIT_PACKAGES, "Project packages": PROJECT_PACKAGES, "Final reel packs": FINAL_REEL_PACKS, "Test console packages": TEST_CONSOLE_PACKAGES}
    for label, folder in sections.items():
        st.markdown(f"### {label}")
        rows = load_package_rows(folder, 30)
        st.metric(f"{label} count", len(rows))
        if rows:
            st.dataframe(display_rows(rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"No {label.lower()} yet.")


def render_backend_status() -> None:
    st.header("Backend status")
    st.caption("Lightweight backend readiness scan. This does not run heavy generation tools.")
    report = scan_backend_queues(limit_per_folder=100)
    summary = report.get("summary", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total packages", summary.get("total", 0))
    c2.metric("Ready", summary.get("ready", 0))
    c3.metric("Blocked", summary.get("blocked", 0))
    c4.metric("Warning only", summary.get("warning_only", 0))
    st.info("Backend adapters are lightweight. Heavy tools are not run from this panel.")
    rows = flatten_backend_rows(report)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No backend package/job JSON files found yet.")
    st.download_button("Download backend scan JSON", data=safe_json_text(report), file_name="naz_lab_backend_scan_report.json", mime="application/json")
    with st.expander("Raw backend scan report", expanded=False):
        st.json(report)


def render_final_packs() -> None:
    st.header("Final reel packs")
    st.caption("Preview and download final reel pack JSON/Markdown manifests. This tab does not render final video.")
    FINAL_REEL_PACKS.mkdir(parents=True, exist_ok=True)
    json_files = latest_files(FINAL_REEL_PACKS, limit=100, pattern="*.json")
    md_files = {path.stem: path for path in latest_files(FINAL_REEL_PACKS, limit=100, pattern="*.md")}
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
    if isinstance(data, dict):
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.metric("Status", str(data.get("status", "")))
        pc2.metric("Images", len(data.get("image_paths", [])))
        pc3.metric("Warnings", len(data.get("warnings", [])))
        pc4.metric("Sources", len(data.get("source_packages", [])))
    st.text_area("Copy final pack JSON", json_text, height=360)
    st.text_area("Copy final pack Markdown", markdown_text, height=300)


def render_package_search() -> None:
    st.header("Package search")
    st.caption("Deep search: filename, path, summary fields, and full nested JSON content are searchable.")
    c1, c2, c3, c4 = st.columns(4)
    folder_label = c1.selectbox("Folder", ["All package folders"] + list(PACKAGE_FOLDERS.keys()))
    project_filter = c2.text_input("Project contains", value="")
    status_filter = c3.text_input("Status contains", value="")
    limit = c4.number_input("Latest files per folder", min_value=5, max_value=500, value=100, step=25)
    keyword = st.text_input("Keyword anywhere in package JSON/file/path", value="")
    folders = PACKAGE_FOLDERS.values() if folder_label == "All package folders" else [PACKAGE_FOLDERS[folder_label]]
    rows: list[dict[str, Any]] = []
    for folder in folders:
        rows.extend(load_package_rows(folder, int(limit)))

    def keep(row: dict[str, Any]) -> bool:
        search_text = str(row.get("SearchText", "")).lower()
        if project_filter and project_filter.lower() not in search_text:
            return False
        if status_filter and status_filter.lower() not in str(row.get("Status", "")).lower():
            return False
        if keyword and keyword.lower() not in search_text:
            return False
        return True

    rows = sorted([row for row in rows if keep(row)], key=lambda item: item.get("Modified", ""), reverse=True)
    st.metric("Matching packages", len(rows))
    if not rows:
        st.info("No matching packages found. Try increasing latest files limit or clearing filters.")
        return
    visible_rows = display_rows(rows)
    st.dataframe(visible_rows, use_container_width=True, hide_index=True)
    report_payload = {"generated_at": datetime.now().isoformat(timespec="seconds"), "filters": {"folder": folder_label, "project": project_filter, "status": status_filter, "keyword": keyword}, "matches": visible_rows}
    report_json = safe_json_text(report_payload)
    report_csv = rows_to_csv(rows)
    report_md = rows_to_markdown(rows)
    export_cols = st.columns(3)
    with export_cols[0]:
        st.download_button("Download report JSON", data=report_json, file_name="naz_lab_package_search_report.json", mime="application/json")
    with export_cols[1]:
        st.download_button("Download report CSV", data=report_csv, file_name="naz_lab_package_search_report.csv", mime="text/csv")
    with export_cols[2]:
        st.download_button("Download report Markdown", data=report_md, file_name="naz_lab_package_search_report.md", mime="text/markdown")
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


def render_launch() -> None:
    st.header("Launch instructions")
    st.write({"Input Test Console": "8508", "Text Workstation": "8501", "Master Dashboard": "8502", "Image Workstation": "8503", "Voice Workstation": "8504", "Video Workstation": "8505", "Portrait Workstation": "8506", "Project Workflow Workstation": "8507"})
    st.code('WORKSTATION="test"  # Input Test Console', language="bash")
    st.code('WORKSTATION="dashboard"  # Master Dashboard', language="bash")
    st.code("streamlit run master_dashboard/app.py --server.port 8502 --server.address 0.0.0.0", language="bash")


def render_roadmap(language: str) -> None:
    st.header("Roadmap")
    st.markdown("""
1. Phase 0 Foundation — complete  
2. Phase 1 Text Workstation — stable  
3. Phase 2 Master Dashboard — stable with deep package search  
4. Phase 3 Image Workstation — stable  
5. Phase 4 Voice Workstation — safer reference manager active  
6. Phase 5 Video Workstation — stable planning/manifest only  
7. Phase 6 Portrait Workstation — safer reference manager active  
8. Input Test Console practical frontend testing — passed  
9. Real content package trials — active
""")
    st.markdown("### Project automation")
    st.json(PROJECT_AUTOMATION_STATUS)
    if language == "Bangla":
        st.markdown("""
পরের কাজের priority:
- True Noir Tales trial verify
- ToolFlow real package trial
- Bangla quality polish যেখানে দরকার
- video generation আলাদা session-এ
""")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Master Dashboard", page_icon="🧪", layout="wide")
    st.title("🧪 Naz Lab Master Control Dashboard")
    st.caption("Phase 2.16 — deep package search, input console aware, backend status, and final pack preview/download")
    update_workstation_status(WORKSTATION_LINKS_JSON, "master_dashboard", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    with st.sidebar:
        st.header("Dashboard settings")
        language = st.radio("Dashboard language note", ["Bangla", "English"], index=0)
        st.caption("Naz Lab default: Bangla-first. Regional default: Rangpur/Nilphamari/North Bengal.")
        st.success("Phase 2.16 stable")
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
