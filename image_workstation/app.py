"""Naz Lab Image Workstation Phase 3.2.

Policy-aware image queue app with Bangladesh defaults, no-sindoor safeguard,
scenario and region selectors, final prompt builder, and manual generator bridge.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import (  # noqa: E402
    BASE_PATH,
    IMAGE_JOBS,
    IMAGE_OUTPUTS,
    IMAGE_PROMPTS,
    OUTPUT_LOG_JSON,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import append_output_log, safe_read_json, safe_write_json, update_workstation_status  # noqa: E402

PHASE = "3.2"
STATUS_OPTIONS = ["pending", "in_progress", "completed", "blocked", "archived"]
PRESET_OPTIONS = ["General Bangladeshi", "True Noir", "ToolFlow", "Rangpur/Nilphamari", "Custom"]
SCENARIO_OPTIONS = ["Auto by context", "Urban Bangladesh", "Rural Bangladesh", "Mixed urban-rural Bangladesh", "Indoor home/office", "Custom"]
REGION_OPTIONS = ["Rangpur/Nilphamari/North Bengal", "Dhaka urban", "Chattogram", "Sylhet", "Noakhali/Comilla", "General Bangladesh", "Custom"]
SINDOOR_OPTIONS = ["No sindoor unless explicitly requested", "Sindoor explicitly requested", "Not applicable"]
GENERATOR_MODES = ["manual_bridge", "future_backend"]

VISUAL_REQUIREMENTS = {
    "Primary culture": "Bangladeshi people and Bangladeshi scenario by default.",
    "Scenario balance": "Use urban, semi-urban, or rural Bangladesh based on context; not only village scenes.",
    "Women sindoor policy": "For women, do not show sindoor unless the prompt explicitly asks for sindoor.",
    "Primary regional flavor": "Rangpur/Nilphamari/North Bengal when regional context is useful.",
    "True Noir style": "Adult-only, cinematic, moody, realistic, no gore, no dead body, no visible wounds.",
    "ToolFlow style": "Clean SaaS/productivity visuals, premium, minimal, practical, non-hype.",
    "Text safety": "Avoid logos, fake official marks, unreadable text clutter, and unnecessary captions inside images.",
}

PRESET_TEXT = {
    "General Bangladeshi": "Bangladeshi people, Bangladeshi environment, realistic cinematic composition, culturally grounded details, natural clothing and setting.",
    "True Noir": "true crime noir cinematic, adult subjects only, Bangladeshi setting, moody light, dramatic shadows, realistic emotional tension, no blood, no gore, no dead body, no visible wounds.",
    "ToolFlow": "clean SaaS productivity visual, premium minimal dashboard feel, modern workspace, practical technology theme, no hype, no clutter.",
    "Rangpur/Nilphamari": "North Bengal / Rangpur / Nilphamari regional atmosphere, grounded Bangladeshi people, rural, small-town, or northern city texture when relevant, natural light, authentic local context.",
    "Custom": "Use the custom direction field as the main visual style instruction.",
}

SCENARIO_TEXT = {
    "Auto by context": "Choose urban, semi-urban, rural, indoor, or outdoor Bangladesh based on the subject and story context.",
    "Urban Bangladesh": "Bangladeshi city setting such as Dhaka/Rangpur/Nilphamari town street, apartment, office, rooftop, cafe, market, bus stop, or modern indoor space.",
    "Rural Bangladesh": "Bangladeshi rural setting with natural local details, but avoid making every image village-only unless context fits.",
    "Mixed urban-rural Bangladesh": "Blend city and regional Bangladesh: small-town street, market, home interior, road, shopfront, or semi-urban neighborhood.",
    "Indoor home/office": "Bangladeshi indoor setting such as apartment, family room, office desk, creator studio, shop, or workstation.",
    "Custom": "Use the custom direction field for scenario details.",
}

REGION_TEXT = {
    "Rangpur/Nilphamari/North Bengal": "Rangpur/Nilphamari/North Bengal flavor where useful; authentic northern Bangladeshi people, small-town or regional urban/rural context.",
    "Dhaka urban": "Dhaka urban context with city streets, apartments, traffic, office, cafe, marketplace, or modern workspace.",
    "Chattogram": "Chattogram context when relevant, port city or hilly/coastal urban feel without stereotypes.",
    "Sylhet": "Sylhet regional context when relevant, green landscape or city/home setting without stereotypes.",
    "Noakhali/Comilla": "Noakhali/Comilla regional context when explicitly useful.",
    "General Bangladesh": "General Bangladeshi cultural and visual context without strong regional markers.",
    "Custom": "Use the custom direction field for region details.",
}

SINDOOR_TEXT = {
    "No sindoor unless explicitly requested": "For women, do not show sindoor. Include sindoor only if the user's prompt explicitly asks for sindoor.",
    "Sindoor explicitly requested": "Sindoor is allowed because the job explicitly requests it.",
    "Not applicable": "No specific sindoor instruction needed for this job.",
}


def read_json(path: Path, default: Any) -> Any:
    try:
        return safe_read_json(path, default)
    except Exception:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default


def list_job_files() -> list[Path]:
    if not IMAGE_JOBS.exists():
        return []
    files = [path for path in IMAGE_JOBS.glob("*.json") if path.is_file()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)


def list_image_files() -> list[Path]:
    if not IMAGE_OUTPUTS.exists():
        return []
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend([path for path in IMAGE_OUTPUTS.glob(pattern) if path.is_file()])
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)


def job_counts(jobs: list[Path]) -> dict[str, int]:
    counts = {status: 0 for status in STATUS_OPTIONS}
    for path in jobs:
        data = read_json(path, {})
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        counts[status] = counts.get(status, 0) + 1
    return counts


def write_job(path: Path, data: dict[str, Any]) -> None:
    data["last_updated"] = datetime.now().isoformat(timespec="seconds")
    safe_write_json(path, data)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="image_workstation",
        event="job_updated",
        details={
            "job_file": str(path),
            "status": data.get("status", "unknown"),
            "preset": data.get("visual_preset", ""),
            "scenario_type": data.get("scenario_type", ""),
            "region_style": data.get("region_style", ""),
        },
    )


def build_final_prompt(
    base_prompt: str,
    preset: str,
    scenario_type: str,
    region_style: str,
    sindoor_policy: str,
    custom_note: str = "",
) -> str:
    parts = [base_prompt.strip()]
    parts.append("Default Bangladesh policy: use Bangladeshi people and a believable Bangladeshi scenario.")
    parts.append(PRESET_TEXT.get(preset, ""))
    parts.append(SCENARIO_TEXT.get(scenario_type, ""))
    parts.append(REGION_TEXT.get(region_style, ""))
    parts.append(SINDOOR_TEXT.get(sindoor_policy, SINDOOR_TEXT["No sindoor unless explicitly requested"]))
    if custom_note.strip():
        parts.append(f"Additional direction: {custom_note.strip()}")
    parts.append("Quality rules: realistic, clean composition, culturally grounded, no fake logos, no unnecessary text inside image, no distorted faces, no extra fingers.")
    return "\n\n".join(part for part in parts if part)


def render_header() -> None:
    st.set_page_config(page_title="Naz Lab Image Workstation", page_icon="🎨", layout="wide")
    st.title("🎨 Naz Lab Image Workstation")
    st.caption("Phase 3.2 — Bangladesh policy, no-sindoor safeguard, scenario/region selectors, final prompt builder.")
    st.info("Bangladeshi people and scenarios by default. Women: no sindoor unless explicitly requested. Urban and rural Bangladesh both supported.")


def render_status() -> None:
    st.header("Status")
    jobs = list_job_files()
    images = list_image_files()
    counts = job_counts(jobs)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Phase", PHASE)
    c2.metric("Job files", len(jobs))
    c3.metric("Pending", counts.get("pending", 0))
    c4.metric("In progress", counts.get("in_progress", 0))
    c5.metric("Image outputs", len(images))

    c6, c7, c8 = st.columns(3)
    c6.metric("Completed", counts.get("completed", 0))
    c7.metric("Blocked", counts.get("blocked", 0))
    c8.metric("Archived", counts.get("archived", 0))

    st.markdown("### Visual requirements")
    st.json(VISUAL_REQUIREMENTS)

    st.markdown("### Policy selectors")
    st.write({
        "scenario_options": SCENARIO_OPTIONS,
        "region_options": REGION_OPTIONS,
        "sindoor_policy_options": SINDOOR_OPTIONS,
        "generator_modes": GENERATOR_MODES,
    })

    with st.expander("Prompt preset details", expanded=False):
        st.json(PRESET_TEXT)
        st.json(SCENARIO_TEXT)
        st.json(REGION_TEXT)

    with st.expander("Paths", expanded=False):
        st.write({
            "base_path": str(BASE_PATH),
            "image_jobs": str(IMAGE_JOBS),
            "image_prompts": str(IMAGE_PROMPTS),
            "image_outputs": str(IMAGE_OUTPUTS),
            "workstation_links_json": str(WORKSTATION_LINKS_JSON),
        })


def render_queue() -> None:
    st.header("Image job queue")
    jobs = list_job_files()
    if not jobs:
        st.info("No image jobs found. Use Text Workstation > Prompt Improver to create image jobs.")
        return

    rows = []
    for path in jobs:
        data = read_json(path, {})
        rows.append({
            "File": path.name,
            "Status": data.get("status", "unknown") if isinstance(data, dict) else "unknown",
            "Preset": data.get("visual_preset", "") if isinstance(data, dict) else "",
            "Scenario": data.get("scenario_type", "") if isinstance(data, dict) else "",
            "Region": data.get("region_style", "") if isinstance(data, dict) else "",
            "Created": data.get("created_at", "") if isinstance(data, dict) else "",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    selected_name = st.selectbox("Select job", [path.name for path in jobs])
    selected_path = IMAGE_JOBS / selected_name
    data = read_json(selected_path, {})
    if not isinstance(data, dict):
        st.error("Selected job JSON could not be read.")
        return

    prompt = data.get("prompt", "")
    current_preset = data.get("visual_preset", "General Bangladeshi")
    current_scenario = data.get("scenario_type", "Auto by context")
    current_region = data.get("region_style", "Rangpur/Nilphamari/North Bengal")
    current_sindoor = data.get("women_sindoor_policy", "No sindoor unless explicitly requested")
    current_generator = data.get("generator_mode", "manual_bridge")

    st.markdown("### Job card")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", data.get("status", "unknown"))
    c2.metric("Preset", current_preset)
    c3.metric("Scenario", current_scenario)
    c4.metric("Region", current_region)

    st.markdown("### Copy-ready base prompt")
    st.text_area("Base prompt", prompt, height=160, help="Original prompt from Text Workstation or prompt library.")

    with st.form("update_job_form"):
        status = st.selectbox("Job status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(data.get("status", "pending")) if data.get("status", "pending") in STATUS_OPTIONS else 0)
        preset = st.selectbox("Visual preset", PRESET_OPTIONS, index=PRESET_OPTIONS.index(current_preset) if current_preset in PRESET_OPTIONS else 0)
        scenario_type = st.selectbox("Scenario type", SCENARIO_OPTIONS, index=SCENARIO_OPTIONS.index(current_scenario) if current_scenario in SCENARIO_OPTIONS else 0)
        region_style = st.selectbox("Region style", REGION_OPTIONS, index=REGION_OPTIONS.index(current_region) if current_region in REGION_OPTIONS else 0)
        sindoor_policy = st.selectbox("Women sindoor policy", SINDOOR_OPTIONS, index=SINDOOR_OPTIONS.index(current_sindoor) if current_sindoor in SINDOOR_OPTIONS else 0)
        generator_mode = st.selectbox("Generator mode", GENERATOR_MODES, index=GENERATOR_MODES.index(current_generator) if current_generator in GENERATOR_MODES else 0)
        custom_direction = st.text_area("Custom / regional / brand direction", value=data.get("custom_direction", ""), height=100)
        final_prompt = build_final_prompt(prompt, preset, scenario_type, region_style, sindoor_policy, custom_direction)
        st.text_area("Final generator-ready prompt", final_prompt, height=260)
        output_path = st.text_input("Output image path", value=data.get("output_path", ""))
        notes = st.text_area("Notes", value=data.get("notes", ""), height=100)
        submitted = st.form_submit_button("Save job update")

    if submitted:
        data["status"] = status
        data["visual_preset"] = preset
        data["scenario_type"] = scenario_type
        data["region_style"] = region_style
        data["bangladesh_default"] = True
        data["women_sindoor_policy"] = sindoor_policy
        data["generator_mode"] = generator_mode
        data["custom_direction"] = custom_direction.strip()
        data["final_prompt"] = final_prompt
        data["enhanced_prompt"] = final_prompt
        data["output_path"] = output_path.strip()
        data["notes"] = notes.strip()
        write_job(selected_path, data)
        st.success("Job updated with final prompt policy fields.")
        st.rerun()

    with st.expander("Raw job JSON", expanded=False):
        st.json(data)


def render_outputs() -> None:
    st.header("Image outputs")
    images = list_image_files()
    if not images:
        st.info("No generated images found yet.")
        st.caption(str(IMAGE_OUTPUTS))
        return

    selected = st.selectbox("Select image", [path.name for path in images])
    path = IMAGE_OUTPUTS / selected
    st.caption(str(path))
    try:
        image = Image.open(path)
        st.image(image, caption=path.name, use_container_width=True)
        st.write({"width": image.width, "height": image.height, "format": image.format})
    except Exception as exc:
        st.error(f"Could not open image: {exc}")


def render_prompt_library() -> None:
    st.header("Prompt library")
    prompt_files = []
    if IMAGE_PROMPTS.exists():
        prompt_files = sorted([path for path in IMAGE_PROMPTS.glob("*.txt") if path.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)
    if not prompt_files:
        st.info("No saved image prompt text files yet.")
        return
    selected = st.selectbox("Select prompt file", [path.name for path in prompt_files])
    path = IMAGE_PROMPTS / selected
    st.caption(str(path))
    st.text_area("Prompt file preview", path.read_text(encoding="utf-8", errors="ignore"), height=320)


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("This Phase 3.2 version creates generator-ready prompts and manages the queue. It does not generate images yet.")
    st.markdown("Next build: generator backend integration after policy workflow is stable.")
    st.code("streamlit run image_workstation/app.py --server.port 8503 --server.address 0.0.0.0", language="bash")


def main() -> None:
    render_header()
    update_workstation_status(
        WORKSTATION_LINKS_JSON,
        "image_workstation",
        {"status": "running", "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")},
    )
    tabs = st.tabs(["Status", "Queue", "Outputs", "Prompt Library", "Launch"])
    with tabs[0]:
        render_status()
    with tabs[1]:
        render_queue()
    with tabs[2]:
        render_outputs()
    with tabs[3]:
        render_prompt_library()
    with tabs[4]:
        render_launch()


if __name__ == "__main__":
    main()
