"""Naz Lab Portrait Workstation Phase 6.4 safer reference manager.

Stable portrait package builder for Bangla-first social portraits,
project presets, safer authorized reference image workflow, output validation,
package metadata, and library previews.
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.drive_paths import BASE_PATH, OUTPUT_LOG_JSON, WORKSTATION_LINKS_JSON  # noqa: E402
from shared.json_utils import append_output_log, safe_read_json, safe_write_json, update_workstation_status  # noqa: E402
from shared.reference_asset_policy import (  # noqa: E402
    PORTRAIT_REFERENCE_ALLOWED_EXTENSIONS,
    PORTRAIT_REFERENCE_POLICY_FIELDS,
    REFERENCE_ALLOWED_USE,
    REFERENCE_ASSET_POLICY,
    REFERENCE_DISALLOWED_USE,
    REFERENCE_MANAGER_UI_REQUIREMENTS,
    is_allowed_reference_extension,
)

PHASE = "6.4"
PHASE_STATUS = "stable-safe-reference-manager"
PORTRAIT_PACKAGES = BASE_PATH / "portrait_packages"
PORTRAIT_OUTPUTS = BASE_PATH / "portrait_outputs"
PORTRAIT_REFERENCES = BASE_PATH / "portrait_references"
IMAGE_JOBS = BASE_PATH / "image_jobs"
IMAGE_OUTPUTS = BASE_PATH / "image_outputs"
IMAGE_EXTENSIONS = set(PORTRAIT_REFERENCE_ALLOWED_EXTENSIONS)

PROJECT_PRESETS = ["General", "True Noir Tales", "ToolFlow", "Personal portrait"]
LANGUAGE_OPTIONS = ["Bangla", "English", "Mixed Bangla-English"]
PORTRAIT_TYPES = ["Profile portrait", "Social media portrait", "Story character portrait", "Creator portrait", "Brand avatar", "Reference-based portrait plan"]
VISUAL_STYLES = ["realistic cinematic", "documentary realistic", "clean professional", "true crime noir", "premium social", "raw mobile-photo style", "editorial portrait", "creator thumbnail portrait"]
SCENARIOS = ["Auto by context", "Urban Bangladesh", "Rangpur/Nilphamari/North Bengal", "Dhaka city", "Office/workstation", "Home interior", "Studio portrait", "Street documentary", "Market/cafe", "Custom"]
FACE_POLICIES = ["Use reference only if user provided one", "No face reference", "Future reference workflow"]
OUTPUT_FORMATS = ["1:1 square", "4:5 portrait", "9:16 vertical", "16:9 wide", "Auto by context"]
MOOD_OPTIONS = ["natural confident", "calm serious", "cinematic tense", "friendly professional", "thoughtful", "premium clean", "emotional but controlled"]
CAMERA_STYLES = ["close-up", "medium portrait", "environmental portrait", "shallow depth of field", "cinematic side light", "natural phone-photo framing"]
PACKAGE_STATUS = ["draft", "ready_for_generation", "generated", "blocked", "archived"]
REFERENCE_REQUIRED_TYPES = {"Reference-based portrait plan"}
REFERENCE_REQUIRED_POLICIES = {"Use reference only if user provided one", "Future reference workflow"}

SAFETY_RULES = {
    "Policy": REFERENCE_ASSET_POLICY,
    "Consent/reference": "Use a personal face/reference image only when the user provides it or explicitly authorizes it for this workflow.",
    "Adults": "Use adult subjects only for content packages unless a safe family/photo-restoration workflow is explicitly designed later.",
    "Bangladesh realism": "Use Bangladeshi people and scenarios by default for general Naz Lab content.",
    "No sindoor default": "For women, no sindoor/vermilion unless explicitly requested.",
    "No gore": "No gore, no dead body, no visible wounds, no exposed violence.",
    "No fake official marks": "Avoid fake logos, fake official uniforms, fake documents, and misleading institutional marks.",
    "No identity guessing": "Do not claim or invent identity for real people in images.",
    "No misleading identity claim": "Do not imply the generated portrait is a real person or verified identity when it is not.",
}

PROJECT_DEFAULTS = {
    "General": {"language": "Bangla", "style": "Bangla-first social portrait planning. Natural, culturally Bangladeshi, Facebook-ready, clean and realistic.", "default_scenario": "Rangpur/Nilphamari/North Bengal", "default_mood": "natural confident"},
    "True Noir Tales": {"language": "English", "style": "English true crime/noir adult character portrait. Moody, cinematic, tense, no gore, no dead body, no visible wounds.", "default_scenario": "Urban Bangladesh", "default_mood": "cinematic tense"},
    "ToolFlow": {"language": "English", "style": "English clean creator/productivity portrait. Professional, modern, premium, practical, non-hype.", "default_scenario": "Office/workstation", "default_mood": "friendly professional"},
    "Personal portrait": {"language": "Bangla", "style": "Reference-aware personal portrait planning. Use only user-provided or explicitly authorized reference, keep natural and respectful.", "default_scenario": "Studio portrait", "default_mood": "natural confident"},
}


def ensure_dirs() -> None:
    for folder in [PORTRAIT_PACKAGES, PORTRAIT_OUTPUTS, PORTRAIT_REFERENCES]:
        folder.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "portrait"


def list_json_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.glob("*.json") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)


def list_image_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.glob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS], key=lambda p: p.stat().st_mtime, reverse=True)


def suggested_output_filename(project: str, portrait_type: str) -> str:
    return f"{safe_name(project)}_{safe_name(portrait_type)}_{now_stamp()}.png"


def validate_image_path(path_text: str, label: str) -> tuple[bool, str]:
    if not path_text.strip():
        return False, f"No {label} path provided yet."
    path = Path(path_text.strip())
    if not path.exists():
        return False, f"{label.title()} file does not exist yet."
    if not is_allowed_reference_extension(path.name, "portrait"):
        return False, f"{label.title()} file exists but extension is not supported."
    return True, f"{label.title()} file exists and looks valid."


def save_uploaded_reference(uploaded_file: Any) -> Path | None:
    if uploaded_file is None:
        return None
    if not is_allowed_reference_extension(uploaded_file.name, "portrait"):
        st.error("Unsupported reference image type. Allowed: " + ", ".join(PORTRAIT_REFERENCE_ALLOWED_EXTENSIONS))
        return None
    ensure_dirs()
    destination = PORTRAIT_REFERENCES / f"reference_image_{now_stamp()}_{safe_name(Path(uploaded_file.name).stem)}{Path(uploaded_file.name).suffix.lower()}"
    with destination.open("wb") as output_file:
        shutil.copyfileobj(uploaded_file, output_file)
    append_output_log(
        OUTPUT_LOG_JSON,
        workstation="portrait_workstation",
        event="reference_image_uploaded",
        details={"path": str(destination), "policy": REFERENCE_ASSET_POLICY},
    )
    return destination


def resolve_reference_path(uploaded_path: Path | None, selected_reference: str, manual_reference_path: str) -> str:
    if uploaded_path:
        return str(uploaded_path)
    if selected_reference and selected_reference != "No saved reference selected":
        return str(PORTRAIT_REFERENCES / selected_reference)
    return manual_reference_path.strip()


def build_reference_metadata(reference_image_path: str, authorized: bool, notes: str, intended_use: str) -> dict[str, Any]:
    metadata = dict(PORTRAIT_REFERENCE_POLICY_FIELDS)
    metadata.update(
        {
            "reference_image_path": reference_image_path,
            "reference_image_authorized": authorized,
            "reference_image_notes": notes.strip(),
            "reference_intended_use": intended_use.strip(),
            "reference_policy": REFERENCE_ASSET_POLICY,
            "reference_allowed_extensions": PORTRAIT_REFERENCE_ALLOWED_EXTENSIONS,
            "reference_policy_phase": "11.0",
            "no_misleading_identity_claim": True,
        }
    )
    return metadata


def reference_required(portrait_type: str, face_policy: str) -> bool:
    return portrait_type in REFERENCE_REQUIRED_TYPES or face_policy in REFERENCE_REQUIRED_POLICIES


def reference_ready_for_package(portrait_type: str, face_policy: str, reference_path: str, authorized: bool) -> tuple[bool, str]:
    if not reference_required(portrait_type, face_policy):
        return True, "Reference image is not required for this portrait mode."
    ref_ok, ref_message = validate_image_path(reference_path, "reference image")
    if not ref_ok:
        return False, ref_message
    if not authorized:
        return False, "Authorization is required before saving a reference-based portrait package."
    return True, "Reference image is valid and authorization is confirmed."


def render_reference_manager(portrait_type: str, face_policy: str) -> tuple[str, bool, str, dict[str, Any], bool, str]:
    st.markdown("### Safer portrait reference manager")
    st.warning("Reference image/face must be user-provided or explicitly authorized. Do not create misleading identity claims.")
    st.caption(f"Reference folder: {PORTRAIT_REFERENCES}")

    with st.expander("Reference Asset Policy", expanded=False):
        st.write(REFERENCE_ASSET_POLICY)
        st.markdown("Allowed use")
        st.json(REFERENCE_ALLOWED_USE)
        st.markdown("Disallowed use")
        st.json(REFERENCE_DISALLOWED_USE)
        st.markdown("Reference manager UI requirements")
        st.json(REFERENCE_MANAGER_UI_REQUIREMENTS)

    uploaded_file = st.file_uploader("Upload authorized reference image", type=[ext.lstrip(".") for ext in PORTRAIT_REFERENCE_ALLOWED_EXTENSIONS])
    uploaded_path = save_uploaded_reference(uploaded_file) if uploaded_file is not None else None
    if uploaded_path:
        st.success(f"Uploaded reference saved: {uploaded_path}")
        st.image(str(uploaded_path), caption="Uploaded authorized reference", use_container_width=False)

    saved_references = list_image_files(PORTRAIT_REFERENCES)
    reference_options = ["No saved reference selected"] + [path.name for path in saved_references]
    selected_reference = st.selectbox("Saved portrait reference images", reference_options)
    manual_reference_path = st.text_input("Selected/manual reference image path", value="")
    reference_path = resolve_reference_path(uploaded_path, selected_reference, manual_reference_path)
    if reference_path:
        st.caption(reference_path)
        ref_preview = Path(reference_path)
        if ref_preview.exists() and ref_preview.is_file():
            st.image(str(ref_preview), caption="Selected reference preview", use_container_width=False)

    reference_authorized = st.checkbox(
        "I confirm this reference image is user-provided or explicitly authorized for this workflow.",
        value=False,
    )
    reference_notes = st.text_area(
        "Reference image notes / intended use",
        height=90,
        placeholder="Example: This is my own photo. Use it only for respectful Bangla portrait planning.",
    )

    metadata = build_reference_metadata(
        reference_image_path=reference_path,
        authorized=reference_authorized,
        notes=reference_notes,
        intended_use="reference-based portrait planning" if reference_required(portrait_type, face_policy) else "portrait planning",
    )
    ref_ready, ref_message = reference_ready_for_package(portrait_type, face_policy, reference_path, reference_authorized)
    if reference_required(portrait_type, face_policy):
        if ref_ready:
            st.success(ref_message)
        else:
            st.error(ref_message)
    elif reference_path and not reference_authorized:
        st.info("Reference path is recorded as non-authorized metadata only; non-reference portrait planning can continue without using it as identity reference.")

    with st.expander("Reference package metadata preview", expanded=False):
        st.json(metadata)
    return reference_path, reference_authorized, reference_notes, metadata, ref_ready, ref_message


def build_style_notes(project: str, language: str, mood: str, camera_style: str, reference_path: str, reference_authorized: bool) -> str:
    notes = [f"Mood: {mood}", f"Camera style: {camera_style}", "Skin texture should look natural, not plastic or over-smoothed.", "Expression should feel human and believable."]
    if reference_path.strip():
        notes.append(f"Reference image path: {reference_path}")
        notes.append(f"Reference authorization confirmed: {reference_authorized}")
        notes.append("Use reference only as user-provided or explicitly authorized guidance for this workflow. Do not make misleading identity claims.")
    if language in {"Bangla", "Mixed Bangla-English"}:
        notes.append("Planning language should support natural Bangla caption/story usage.")
    if project == "True Noir Tales":
        notes.append("Use noir lighting, emotional tension, adult character framing, and subtle storytelling details.")
    if project == "ToolFlow":
        notes.append("Use clean workspace, productivity/AI context, premium minimal look, and non-hype creator framing.")
    if project == "Personal portrait":
        notes.append("Keep respectful, natural, and consistent with user-provided or explicitly authorized reference only.")
    return "\n".join(notes)


def build_positive_prompt(project: str, language: str, portrait_type: str, style: str, scenario: str, face_policy: str, output_format: str, mood: str, camera_style: str, reference_path: str, reference_authorized: bool, topic: str, custom_note: str) -> str:
    style_notes = build_style_notes(project, language, mood, camera_style, reference_path, reference_authorized)
    parts = [
        f"Project preset: {project}", f"Language/planning: {language}", f"Portrait type: {portrait_type}", f"Visual style: {style}", f"Scenario: {scenario}", f"Mood: {mood}", f"Camera style: {camera_style}", f"Face/reference policy: {face_policy}", f"Reference image path: {reference_path or '[not selected]'}", f"Reference authorized: {reference_authorized}", f"Output format: {output_format}", f"Project style: {PROJECT_DEFAULTS[project]['style']}",
        "Bangla-first rule: General Naz Lab planning defaults to Bangla; English is used for selected English projects or when requested.",
        "Create a realistic, natural, culturally grounded portrait plan with adult subjects only.",
        "Bangladeshi people and Bangladeshi scenario by default for General Naz Lab content.",
        "Urban and rural Bangladesh are both allowed depending on scenario.",
        "For women, no sindoor or vermilion in hair parting unless explicitly requested.",
        f"Reference policy: {REFERENCE_ASSET_POLICY}",
        style_notes,
    ]
    if project == "True Noir Tales":
        parts.append("True Noir Tales portrait rule: moody true-crime noir, adult character, emotional tension, no gore, no dead body, no visible wounds, no exposed violence.")
    if project == "ToolFlow":
        parts.append("ToolFlow portrait rule: clean modern professional creator/productivity feel, premium but non-hype, practical and trustworthy.")
    if topic.strip():
        parts.append(f"Source/topic:\n{topic.strip()}")
    if custom_note.strip():
        parts.append(f"Custom direction:\n{custom_note.strip()}")
    return "\n\n".join(parts)


def build_negative_prompt(project: str) -> str:
    base = ["no gore", "no dead body", "no visible wounds", "no exposed violence", "no distorted face", "no extra fingers", "no fake logo", "no watermark", "no unreadable text", "no sindoor unless explicitly requested", "no vermilion unless explicitly requested", "no misleading official uniform or document", "no misleading identity claim", "no fake celebrity likeness", "no unauthorized face reference", "no plastic skin", "no over-smoothed face"]
    if project == "True Noir Tales":
        base.extend(["no blood", "no weapon focus", "no sensational violence"])
    return ", ".join(base)


def build_package(project: str, language: str, portrait_type: str, style: str, scenario: str, face_policy: str, reference_path: str, reference_authorized: bool, reference_notes: str, reference_metadata: dict[str, Any], output_format: str, mood: str, camera_style: str, status: str, output_path: str, positive: str, negative: str) -> dict[str, Any]:
    package = {"created_at": datetime.now().isoformat(timespec="seconds"), "phase": PHASE, "project_preset": project, "language": language, "portrait_type": portrait_type, "visual_style": style, "scenario": scenario, "mood": mood, "camera_style": camera_style, "face_policy": face_policy, "reference_image_path": reference_path, "reference_image_authorized": reference_authorized, "reference_image_notes": reference_notes.strip(), "output_format": output_format, "status": status, "suggested_output_path": output_path, "positive_prompt": positive, "negative_prompt": negative, "combined_prompt": f"POSITIVE PROMPT:\n{positive}\n\nNEGATIVE PROMPT:\n{negative}", "future_backend": "placeholder"}
    package.update(reference_metadata)
    return package


def save_package(package: dict[str, Any]) -> Path:
    ensure_dirs()
    path = PORTRAIT_PACKAGES / f"portrait_package_{safe_name(package['project_preset'])}_{now_stamp()}.json"
    safe_write_json(path, package)
    append_output_log(OUTPUT_LOG_JSON, workstation="portrait_workstation", event="portrait_package_saved", details={"path": str(path), "project": package["project_preset"], "status": package["status"], "reference_image_authorized": package.get("reference_image_authorized", False)})
    return path


def render_status() -> None:
    st.header("Status")
    ensure_dirs()
    packages = list_json_files(PORTRAIT_PACKAGES)
    outputs = list_image_files(PORTRAIT_OUTPUTS)
    references = list_image_files(PORTRAIT_REFERENCES)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Phase", PHASE); c2.metric("Status", PHASE_STATUS); c3.metric("Packages", len(packages)); c4.metric("Outputs", len(outputs)); c5.metric("References", len(references))
    st.success("Portrait Workstation status: stable with safer reference manager")
    st.markdown("### Stable workflow")
    st.markdown("1. Pick project preset and portrait type.  \n2. Select language, visual style, mood, camera, and scenario.  \n3. Upload/select authorized reference image only when needed.  \n4. Confirm authorization and add notes for reference-based workflow.  \n5. Copy prompt or save package JSON.  \n6. Save generated output later into portrait_outputs.")
    st.markdown("### Safety rules"); st.json(SAFETY_RULES)
    with st.expander("Project defaults", expanded=False): st.json(PROJECT_DEFAULTS)
    with st.expander("Paths", expanded=False): st.write({"portrait_packages": str(PORTRAIT_PACKAGES), "portrait_outputs": str(PORTRAIT_OUTPUTS), "portrait_references": str(PORTRAIT_REFERENCES), "image_jobs": str(IMAGE_JOBS), "image_outputs": str(IMAGE_OUTPUTS)})


def render_builder() -> None:
    st.header("Portrait package builder")
    project = st.selectbox("Project preset", PROJECT_PRESETS)
    defaults = PROJECT_DEFAULTS[project]
    language = st.selectbox("Language", LANGUAGE_OPTIONS, index=LANGUAGE_OPTIONS.index(defaults["language"]))
    portrait_type = st.selectbox("Portrait type", PORTRAIT_TYPES)
    style = st.selectbox("Visual style", VISUAL_STYLES)
    default_scenario = defaults["default_scenario"] if defaults["default_scenario"] in SCENARIOS else "Auto by context"
    scenario = st.selectbox("Scenario", SCENARIOS, index=SCENARIOS.index(default_scenario))
    mood = st.selectbox("Mood", MOOD_OPTIONS, index=MOOD_OPTIONS.index(defaults["default_mood"]))
    camera_style = st.selectbox("Camera style", CAMERA_STYLES)
    face_policy = st.selectbox("Face/reference policy", FACE_POLICIES)
    reference_path, reference_authorized, reference_notes, reference_metadata, ref_ready, ref_message = render_reference_manager(portrait_type, face_policy)
    output_format = st.selectbox("Output format", OUTPUT_FORMATS)
    status = st.selectbox("Package status", PACKAGE_STATUS)
    suggested_output = PORTRAIT_OUTPUTS / suggested_output_filename(project, portrait_type)
    output_path = st.text_input("Suggested portrait output path", value=str(suggested_output))
    out_ok, out_message = validate_image_path(output_path, "portrait output")
    st.success(out_message) if out_ok else st.warning(out_message)
    topic = st.text_area("Source topic / character description", height=150, placeholder="Describe the person/character/brand portrait need here.")
    custom_note = st.text_area("Custom portrait direction", height=100, placeholder="Example: more professional, more emotional, more North Bengal realism, etc.")
    positive = build_positive_prompt(project, language, portrait_type, style, scenario, face_policy, output_format, mood, camera_style, reference_path, reference_authorized, topic, custom_note)
    negative = build_negative_prompt(project)
    package = build_package(project, language, portrait_type, style, scenario, face_policy, reference_path, reference_authorized, reference_notes, reference_metadata, output_format, mood, camera_style, status, output_path, positive, negative)
    st.markdown("### Reference workflow note")
    st.warning("Use a face/image reference only when the user provides or explicitly authorizes it. Do not assume or invent a specific real person's face.")
    st.text_area("Positive prompt", positive, height=300)
    st.text_area("Negative prompt", negative, height=130)
    st.text_area("Combined prompt", package["combined_prompt"], height=380)
    with st.expander("Portrait package JSON preview", expanded=False): st.json(package)
    if st.button("Save portrait package JSON"):
        if reference_required(portrait_type, face_policy) and not ref_ready:
            st.error(f"Cannot save reference-based portrait package: {ref_message}")
        else:
            st.success(f"Saved: {save_package(package)}")


def render_library() -> None:
    st.header("Portrait package library")
    ensure_dirs()
    packages = list_json_files(PORTRAIT_PACKAGES); outputs = list_image_files(PORTRAIT_OUTPUTS); references = list_image_files(PORTRAIT_REFERENCES)
    st.metric("Packages", len(packages)); st.metric("Outputs", len(outputs)); st.metric("References", len(references))
    if packages:
        selected = st.selectbox("Select package", [p.name for p in packages])
        st.json(safe_read_json(PORTRAIT_PACKAGES / selected, {}))
    if outputs:
        st.markdown("### Output files")
        for item in outputs[:10]:
            st.write(str(item))
            st.image(str(item), use_container_width=False)
    if references:
        st.markdown("### Reference files")
        selected_reference = st.selectbox("Preview reference", [p.name for p in references])
        ref_path = PORTRAIT_REFERENCES / selected_reference
        st.caption(str(ref_path))
        st.image(str(ref_path), use_container_width=False)
    if not packages: st.info("No portrait packages saved yet.")


def render_inputs() -> None:
    st.header("Input placeholders")
    st.markdown("Future versions may connect image jobs, portrait references, and generated outputs directly.")
    image_jobs = list_json_files(IMAGE_JOBS); image_outputs = list_image_files(IMAGE_OUTPUTS)
    st.write({"image_job_count": len(image_jobs), "image_output_count": len(image_outputs)})
    if image_jobs:
        selected_job = st.selectbox("Preview image job", [p.name for p in image_jobs])
        st.json(safe_read_json(IMAGE_JOBS / selected_job, {}))


def render_launch() -> None:
    st.header("Launch notes")
    st.markdown("Portrait Workstation Phase 6.4 is stable with a safer reference manager for authorized portrait/reference image planning. It does not generate or swap faces.")
    st.markdown("Next recommended build: Dashboard Package Search download/export buttons.")
    st.code("streamlit run portrait_workstation/app.py --server.port 8506 --server.address 0.0.0.0", language="bash")


def main() -> None:
    st.set_page_config(page_title="Naz Lab Portrait Workstation", page_icon="🧑", layout="wide")
    st.title("🧑 Naz Lab Portrait Workstation")
    st.caption("Phase 6.4 stable — safer reference manager, portrait prompts, output metadata, package library.")
    st.success("Portrait Workstation status: stable with safer reference manager")
    st.info("Bangla-first planning. Use face/image references only when the user provides or explicitly authorizes them for this workflow.")
    ensure_dirs()
    update_workstation_status(WORKSTATION_LINKS_JSON, "portrait_workstation", {"status": PHASE_STATUS, "phase": PHASE, "last_seen": datetime.now().isoformat(timespec="seconds")})
    tabs = st.tabs(["Status", "Builder", "Inputs", "Library", "Launch"])
    with tabs[0]: render_status()
    with tabs[1]: render_builder()
    with tabs[2]: render_inputs()
    with tabs[3]: render_library()
    with tabs[4]: render_launch()


if __name__ == "__main__":
    main()
