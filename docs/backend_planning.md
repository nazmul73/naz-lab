# Naz Lab Backend Planning

Phase: Backend Planning Foundation 1.0
Status: planning-ready

## Purpose

Naz Lab is a Bangla-first content creation workstation ecosystem. The current Streamlit workstations prepare prompts, packages, metadata, references, and exports. Backend planning defines how heavy generation tools should be connected later without breaking the stable workstation flow.

The goal is not to install heavy tools inside the Master Dashboard. The goal is to keep each generation backend isolated, testable, and recoverable in Colab or a future hosted runtime.

## Core rule

Backend tools should be connected only after the planning, package, safety, and export workflows are stable.

The Master Dashboard remains a control center. Heavy AI generation stays in separate workstation runtimes or backend services.

## Current stable frontend/workstation layer

- Text Workstation: Bangla-first writing, scripts, captions, prompt improvement.
- Master Dashboard: status, links, output folders, job/package search, JSON/CSV/Markdown export.
- Image Workstation: image prompt and image job planning.
- Voice Workstation: narration/TTS direction and safer authorized reference voice metadata.
- Video Workstation: scene, video, and reel package planning.
- Portrait Workstation: portrait package planning and safer authorized reference image metadata.
- Project Workflow Workstation: one-topic-to-full-package planning for True Noir Tales, ToolFlow, and General Bangla.

## Backend candidates by workflow

### Text backend

Current direction:

- Ollama in Colab or local runtime.
- Drive-persisted model folder.
- Lightweight default model for reliability.

Future candidates:

- Ollama local/Colab models.
- OpenAI or other API model adapter if user chooses later.

Backend interface:

```json
{
  "input_text": "topic or draft",
  "language": "Bangla",
  "regional_tone": "Rangpur/Nilphamari",
  "project_preset": "General Bangla",
  "output_type": "script/post/caption/package"
}
```

### Image backend

Current direction:

- Workstation prepares prompts and image jobs.
- Generation backend should read saved image job JSON.

Future candidates:

- Fooocus in a separate Colab runtime.
- Stable Diffusion / SDXL runtime.
- API-based image backend if selected later.

Backend interface:

```json
{
  "positive_prompt": "...",
  "negative_prompt": "...",
  "output_format": "1:1 square",
  "project_preset": "True Noir Tales",
  "safety_rules": {
    "adult_only": true,
    "no_gore": true,
    "no_visible_wounds": true
  }
}
```

Output target:

```text
/content/drive/MyDrive/NazLab/image_outputs
```

### Voice backend

Current direction:

- Voice Workstation prepares scripts, narration direction, TTS direction, package JSON, and authorized reference metadata.
- Real TTS or voice clone backend should check reference authorization before using any reference audio.

Future candidates:

- Basic TTS backend for generic narration.
- XTTS v2 or similar reference-voice backend in separate runtime.
- API-based TTS backend if selected later.

Required safety check before reference voice generation:

```json
{
  "reference_voice_path": "...",
  "reference_voice_authorized": true,
  "reference_policy": "Reference voice requires user-provided or explicitly authorized audio."
}
```

If `reference_voice_authorized` is not true, backend must not use the reference voice.

Output target:

```text
/content/drive/MyDrive/NazLab/audio_outputs
/content/drive/MyDrive/NazLab/voice_outputs
```

### Video backend

Current direction:

- Video Workstation prepares scene plans, video prompts, and reel package metadata.
- Backend should remain separate because video generation is heavy and tool-specific.

Future candidates:

- Image-to-video runtime.
- FFmpeg assembly backend.
- External video API adapter.

Backend interface:

```json
{
  "scene_list": [],
  "image_paths": [],
  "voice_path": "...",
  "caption": "...",
  "platform": "Facebook Reels",
  "duration_seconds": 60
}
```

Output target:

```text
/content/drive/MyDrive/NazLab/video_outputs
```

### Portrait backend

Current direction:

- Portrait Workstation prepares portrait prompts, reference image metadata, and package JSON.
- Real face, portrait, animation, or swap backend must check authorization metadata first.

Future candidates:

- LivePortrait in separate runtime.
- FaceFusion in separate runtime.
- Portrait enhancement or animation adapter.

Required safety check before reference image use:

```json
{
  "reference_image_path": "...",
  "reference_image_authorized": true,
  "reference_policy": "Reference image requires user-provided or explicitly authorized image.",
  "no_misleading_identity_claim": true
}
```

If `reference_image_authorized` is not true, backend must not use the reference image as an identity/face reference.

Output target:

```text
/content/drive/MyDrive/NazLab/portrait_outputs
```

## Backend adapter pattern

Each backend should follow this minimal pattern:

1. Read package/job JSON from Drive.
2. Validate required fields.
3. Validate safety metadata.
4. Run generation or planning step.
5. Save output to the correct Drive folder.
6. Append an output log entry.
7. Update package/job status.
8. Never corrupt existing JSON files.

Suggested backend adapter function names:

```text
load_package()
validate_package()
validate_reference_policy()
run_backend()
save_outputs()
append_backend_log()
mark_package_status()
```

## Backend queue status model

Recommended statuses:

```text
draft
ready_for_backend
running
completed
blocked
failed
archived
```

Blocked examples:

- missing source file
- missing output folder
- unsupported file extension
- reference asset not authorized
- GPU not available for a GPU-only backend
- required token/API key missing

## Colab/runtime strategy

Use one runtime per heavy backend when needed:

- Dashboard runtime: lightweight only.
- Text runtime: Ollama/text dependencies.
- Image runtime: Fooocus/SDXL dependencies.
- Voice runtime: TTS/XTTS dependencies.
- Video runtime: video/FFmpeg/model dependencies.
- Portrait runtime: LivePortrait/FaceFusion dependencies.

Do not install all heavy tools in one runtime unless a dedicated all-in-one generation runtime is intentionally designed later.

## Safety gates

Before any backend generation:

- Check project safety rules.
- Check reference asset authorization.
- Check allowed extensions.
- Check output folder exists.
- Check package status is ready.
- Check backend-specific hardware requirements.

Reference assets must follow:

```text
shared/reference_asset_policy.py
```

## Bangla-first backend requirement

Backend output should preserve Bangla-first content priority.

For Bangla scripts and voice:

- natural spoken Bangla
- simple sentence flow
- Facebook-ready
- voiceover-ready
- not stiff textbook Bangla
- default regional flavor: Rangpur / Nilphamari / North Bengal when requested or appropriate

## Immediate next backend planning actions

1. Add backend package schema docs.
2. Add lightweight backend adapter skeletons without installing heavy tools.
3. Add backend status/checklist page to Dashboard if needed.
4. Add Colab runbooks only when a real backend is selected for testing.
5. Start with the safest backend first: generic TTS or image prompt-to-output adapter.

## Test policy

No heavy backend test is required for this planning document.

When real backend code is added later, the user should run the relevant Colab command and share output/error.
