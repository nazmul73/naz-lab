"""Naz Lab Image Workstation Phase 3.3.

Unified preset image prompt builder for project presets, content types,
naturalness controls, scene realism, and positive/negative prompt output.
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

PHASE = "3.3"
STATUS_OPTIONS = ["pending", "in_progress", "completed", "blocked", "archived"]
PROJECT_PRESETS = ["True Noir Tales", "ToolFlow", "General"]
CONTENT_TYPES = ["General Facebook post", "Reel thumbnail", "Carousel cover", "Story scene"]
NATURALNESS_LEVELS = ["Documentary realistic", "Cinematic realistic", "Social media realistic", "Premium ad-style", "Raw mobile-photo style"]
SCENARIO_OPTIONS = ["Auto by context", "Urban Bangladesh", "Rural Bangladesh", "Mixed urban-rural Bangladesh", "Indoor home/office", "Custom"]
LOCATION_TYPES = ["Auto by context", "Dhaka city street", "Rangpur/Nilphamari town", "Semi-urban neighborhood", "Village road", "Apartment interior", "Office/workstation", "Rooftop", "Market", "Cafe", "Studio", "Home interior", "Custom"]
REGION_OPTIONS = ["Rangpur/Nilphamari/North Bengal", "Dhaka urban", "Chattogram", "Sylhet", "Noakhali/Comilla", "General Bangladesh", "Custom"]
CHARACTER_TYPES = ["adult Bangladeshi woman", "adult Bangladeshi man", "young professional", "office worker", "creator", "narrator-type subject", "mixed adult group", "Auto by context"]
CLOTHING_STYLES = ["auto by context", "everyday Bangladeshi casual", "office wear", "salwar kameez", "saree without sindoor by default", "urban modest wear", "smart casual"]
EXPRESSIONS = ["auto by context", "worried", "tense", "thoughtful", "focused", "shocked", "calm", "emotionally controlled", "curious"]
CAMERA_STYLES = ["auto by context", "smartphone photo", "cinematic close-up", "medium shot", "street documentary", "shallow depth of field", "over-the-shoulder", "workspace shot"]
SINDOOR_OPTIONS = ["No sindoor unless explicitly requested", "Sindoor explicitly requested", "Not applicable"]
ASPECT_RATIOS = ["1:1 square post", "9:16 reel/story", "4:5 portrait post", "16:9 wide", "Auto by context"]
GENERATOR_MODES = ["manual_bridge", "future_backend"]

VISUAL_REQUIREMENTS = {
    "Project preset layer": "True Noir Tales, ToolFlow, or General controls brand identity.",
    "Content type layer": "General Facebook post, Reel thumbnail, Carousel cover, or Story scene controls asset purpose.",
    "Bangladesh default": "Use Bangladeshi people and Bangladeshi scenario by default.",
    "Scenario balance": "Use urban, semi-urban, or rural Bangladesh based on context; not only village scenes.",
    "Women sindoor policy": "For women, do not show sindoor unless the prompt explicitly asks for sindoor.",
    "Primary regional flavor": "Rangpur/Nilphamari/North Bengal when regional context is useful.",
    "English projects": "True Noir Tales and ToolFlow are English content projects by default.",
}

PROJECT_TEXT = {
    "True Noir Tales": "English true crime / noir storytelling brand style, cinematic suspense, adult-only human-centered scene, emotional tension, moody lighting, no gore, no dead body, no visible wounds.",
    "ToolFlow": "English AI tools / SaaS / productivity brand style, clean premium modern workspace, dashboard or workflow feel, practical, trustworthy, non-hype, minimal clutter.",
    "General": "Flexible general social content visual, culturally grounded, natural and platform-ready.",
}

CONTENT_TYPE_TEXT = {
    "General Facebook post": "Balanced social post composition, clear focal subject, suitable for Facebook/Instagram feed.",
    "Reel thumbnail": "High-click thumbnail composition, strong focal point, clear emotion or idea, bold visual hierarchy, instantly understandable.",
    "Carousel cover": "Clean cover-first layout, headline-friendly negative space, premium minimal composition, strong first-slide feel.",
    "Story scene": "Narrative scene composition with environment storytelling, cinematic or documentary moment, human-centered visual context.",
}

NATURALNESS_TEXT = {
    "Documentary realistic": "documentary realistic, natural imperfections, believable human expressions, grounded lighting.",
    "Cinematic realistic": "cinematic realistic, polished lighting, shallow depth of field, premium social media composition.",
    "Social media realistic": "social media realistic, natural but polished, scroll-stopping composition without looking fake.",
    "Premium ad-style": "premium ad-style, clean composition, refined lighting, high-end visual clarity.",
    "Raw mobile-photo style": "raw mobile-photo style, candid framing, natural light, realistic everyday look.",
}

SCENARIO_TEXT = {
    "Auto by context": "Choose urban, semi-urban, rural, indoor, or outdoor Bangladesh based on the subject and story context.",
    "Urban Bangladesh": "Bangladeshi city or town setting such as street, apartment, office, rooftop, cafe, market, bus stop, or modern indoor space.",
    "Rural Bangladesh": "Bangladeshi rural setting with natural local details, only when context fits.",
    "Mixed urban-rural Bangladesh": "Small-town or semi-urban Bangladesh: market, home interior, road, shopfront, neighborhood, or regional town.",
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
    "No sindoor unless explicitly requested": "For women, no sindoor, no vermilion in the hair parting. Include sindoor only if explicitly requested.",
    "Sindoor explicitly requested": "Sindoor is allowed because the job explicitly requests it.",
    "Not applicable": "No specific sindoor instruction needed for this job.",
}

DEFAULT_NEGATIVE = "no sindoor unless explicitly requested, no vermilion in hair parting unless requested, no Indian wedding look unless requested, no Bollywood styling, no fantasy costume, no fake logo, no watermark, no unreadable text, no distorted face, no extra fingers, no gore, no dead body, no visible wounds"


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
            "project_preset": data.get("project_preset", ""),
            "content_type": data.get("content_type", ""),
            "region_style": data.get("region_style", ""),
        },
    )


def build_positive_prompt(data: dict[str, Any], base_prompt: str) -> str:
    project = data.get("project_preset", "General")
    content_type = data.get("content_type", "General Facebook post")
    naturalness = data.get("naturalness_level", "Cinematic realistic")
    scenario = data.get("scenario_type", "Auto by context")
    location = data.get("location_type", "Auto by context")
    region = data.get("region_style", "Rangpur/Nilphamari/North Bengal")
    character = data.get("character_type", "Auto by context")
    clothing = data.get("clothing_style", "auto by context")
    expression = data.get("expression", "auto by context")
    camera = data.get("camera_style", "auto by context")
    sindoor = data.get("women_sindoor_policy", "No sindoor unless explicitly requested")
    aspect = data.get("aspect_ratio", "1:1 square post")
    custom = data.get("custom_direction", "")

    parts = [
        base_prompt.strip(),
        "Default Bangladesh policy: Bangladeshi people and a believable Bangladeshi scenario.",
        PROJECT_TEXT.get(project, ""),
        CONTENT_TYPE_TEXT.get(content_type, ""),
        NATURALNESS_TEXT.get(naturalness, ""),
        SCENARIO_TEXT.get(scenario, ""),
        f"Location type: {location}.",
        REGION_TEXT.get(region, ""),
        f"Character type: {character}.",
        f"Clothing style: {clothing}.",
        f"Expression: {expression}.",
        f"Camera style: {camera}.",
        SINDOOR_TEXT.get(sindoor, SINDOOR_TEXT["No sindoor unless explicitly requested"]),
        f"Output format: {aspect}.",
    ]
    if custom.strip():
        parts.append(f"Additional direction: {custom.strip()}")
    parts.append("Quality rules: realistic, clean composition, culturally grounded, no fake logos, no unnecessary text inside image, no distorted faces, no extra fingers.")
    return "\n\n".join(part for part in parts if part)


def build_negative_prompt(data: dict[str, Any]) -> str:
    extra_negative = data.get("extra_negative_prompt", "")
    parts = [DEFAULT_NEGATIVE]
    if extra_negative.strip():
        parts.append(extra_negative.strip())
    return ", ".join(parts)


def build_combined_prompt(positive: str, negative: str) -> str:
    return f"POSITIVE PROMPT:\n{positive}\n\nNEGATIVE PROMPT:\n{negative}"


def render_header() -> None:
    st.set_page_config(page_title="Naz Lab Image Workstation", page_icon="🎨", layout="wide")
    st.title("🎨 Naz Lab Image Workstation")
    st.caption("Phase 3.3 — project presets, content types, natural image controls, positive/negative prompt builder.")
    st.info("True Noir Tales and ToolFlow are English projects. Bangladesh visuals by default. Women: no sindoor unless explicitly requested.")


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

    st.markdown("### Unified preset layers")
    st.write({
        "project_presets": PROJECT_PRESETS,
        "content_types": CONTENT_TYPES,
        "naturalness_levels": NATURALNESS_LEVELS,
        "scenario_options": SCENARIO_OPTIONS,
        "location_types": LOCATION_TYPES,
        "region_options": REGION_OPTIONS,
    })

    with st.expander("Preset text details", expanded=False):
        st.json(PROJECT_TEXT)
        st.json(CONTENT_TYPE_TEXT)
        st.json(NATURALNESS_TEXT)

    with st.expander("Paths", expanded=False):
        st.write({
            "base_path": str(BASE_PATH),
            "image_jobs": str(IMAGE_JOBS),
            "image_prompts": str(IMAGE_PROMPTS),
            "image_outputs": str(IMAGE_OUTPUTS),
            "workstation_links_json": str(WORKSTATION_LINKS_JSON),
        })


def select_index(options: list[str], value: str, fallback: int = 0) -> int:
    return options.index(value) if value in options else fallback


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
            "Project": data.get("project_preset", data.get("visual_preset", "")) if isinstance(data, dict) else "",
            "Content type": data.get("content_type", "") if isinstance(data, dict) else "",
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
    st.markdown("### Job card")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", data.get("status", "unknown"))
    c2.metric("Project", data.get("project_preset", data.get("visual_preset", "General")))
    c3.metric("Content", data.get("content_type", "General Facebook post"))
    c4.metric("Region", data.get("region_style", "Rangpur/Nilphamari/North Bengal"))

    st.markdown("### Copy-ready base prompt")
    st.text_area("Base prompt", prompt, height=140, help="Original prompt from Text Workstation or prompt library.")

    with st.form("update_job_form"):
        status = st.selectbox("Job status", STATUS_OPTIONS, index=select_index(STATUS_OPTIONS, data.get("status", "pending")))
        project_preset = st.selectbox("Project preset", PROJECT_PRESETS, index=select_index(PROJECT_PRESETS, data.get("project_preset", "General"), fallback=2))
        content_type = st.selectbox("Content type", CONTENT_TYPES, index=select_index(CONTENT_TYPES, data.get("content_type", "General Facebook post")))
        naturalness = st.selectbox("Naturalness level", NATURALNESS_LEVELS, index=select_index(NATURALNESS_LEVELS, data.get("naturalness_level", "Cinematic realistic"), fallback=1))
        scenario_type = st.selectbox("Scenario type", SCENARIO_OPTIONS, index=select_index(SCENARIO_OPTIONS, data.get("scenario_type", "Auto by context")))
        location_type = st.selectbox("Location type", LOCATION_TYPES, index=select_index(LOCATION_TYPES, data.get("location_type", "Auto by context")))
        region_style = st.selectbox("Region style", REGION_OPTIONS, index=select_index(REGION_OPTIONS, data.get("region_style", "Rangpur/Nilphamari/North Bengal")))
        character_type = st.selectbox("Character type", CHARACTER_TYPES, index=select_index(CHARACTER_TYPES, data.get("character_type", "Auto by context"), fallback=len(CHARACTER_TYPES) - 1))
        clothing_style = st.selectbox("Clothing style", CLOTHING_STYLES, index=select_index(CLOTHING_STYLES, data.get("clothing_style", "auto by context")))
        expression = st.selectbox("Expression", EXPRESSIONS, index=select_index(EXPRESSIONS, data.get("expression", "auto by context")))
        camera_style = st.selectbox("Camera style", CAMERA_STYLES, index=select_index(CAMERA_STYLES, data.get("camera_style", "auto by context")))
        sindoor_policy = st.selectbox("Women sindoor policy", SINDOOR_OPTIONS, index=select_index(SINDOOR_OPTIONS, data.get("women_sindoor_policy", "No sindoor unless explicitly requested")))
        aspect_ratio = st.selectbox("Aspect ratio", ASPECT_RATIOS, index=select_index(ASPECT_RATIOS, data.get("aspect_ratio", "1:1 square post")))
        generator_mode = st.selectbox("Generator mode", GENERATOR_MODES, index=select_index(GENERATOR_MODES, data.get("generator_mode", "manual_bridge")))
        custom_direction = st.text_area("Custom / regional / brand direction", value=data.get("custom_direction", ""), height=90)
        extra_negative = st.text_area("Extra negative prompt", value=data.get("extra_negative_prompt", ""), height=70)

        temp_data = dict(data)
        temp_data.update({
            "project_preset": project_preset,
            "content_type": content_type,
            "naturalness_level": naturalness,
            "scenario_type": scenario_type,
            "location_type": location_type,
            "region_style": region_style,
            "character_type": character_type,
            "clothing_style": clothing_style,
            "expression": expression,
            "camera_style": camera_style,
            "women_sindoor_policy": sindoor_policy,
            "aspect_ratio": aspect_ratio,
            "generator_mode": generator_mode,
            "custom_direction": custom_direction.strip(),
            "extra_negative_prompt": extra_negative.strip(),
        })
        positive_prompt = build_positive_prompt(temp_data, prompt)
        negative_prompt = build_negative_prompt(temp_data)
        combined_prompt = build_combined_prompt(positive_prompt, negative_prompt)

        st.text_area("Final positive prompt", positive_prompt, height=220)
        st.text_area("Final negative prompt", negative_prompt, height=120)
        st.text_area("Copy-ready combined prompt", combined_prompt, height=260)

        output_path = st.text_input("Output image path", value=data.get("output_path", ""))
        notes = st.text_area("Notes", value=data.get("notes", ""), height=90)
        submitted = st.form_submit_button("Save job update")

    if submitted:
        data.update(temp_data)
        data["status"] = status
        data["visual_preset"] = project_preset
        data["bangladesh_default"] = True
        data["final_positive_prompt"] = positive_prompt
        data["final_negative_prompt"] = negative_prompt
        data["combined_prompt"] = combined_prompt
        data["final_prompt"] = combined_prompt
        data["enhanced_prompt"] = combined_prompt
        data["output_path"] = output_path.strip()
        data["notes"] = notes.strip()
        write_job(selected_path, data)
        st.success("Job updated with unified preset prompts.")
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
    st.markdown("This Phase 3.3 version creates positive/negative generator-ready prompts. It does not generate images yet.")
    st.markdown("Next build: manual generator bridge with completion helpers, then backend integration.")
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
