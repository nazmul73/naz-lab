# Naz Lab AI Workstation

Naz Lab is a modular AI content production lab for Google Colab, Streamlit, Google Drive, Ollama, and future creative backends.

## Current vision

Naz Lab is designed around this workflow:

```text
Idea / Topic
-> Text package
-> Image prompt package
-> Voice package
-> Video package
-> Portrait package
-> Final posting package
```

The system is modular. Each workstation runs as a separate Streamlit app in Colab, while Google Drive stores outputs and JSON packages.

## Global language rule

Naz Lab is Bangla-first by default.

Priority:

1. Bangla
2. English
3. Other languages optional

Bangla must be:

- natural spoken Bangla
- Facebook-ready
- netizen-friendly
- voiceover-ready
- subtitle-friendly when used in video
- simple and human
- not stiff textbook Bangla

Default regional flavor:

- Rangpur / Nilphamari / North Bengal

Secondary regional tones are supported when requested:

- Dhakaiya
- Chattogram
- Sylhet
- Noakhali / Comilla

True Noir Tales and ToolFlow can remain English-first project presets when selected.

## Current workstation stack

| Workstation | Phase | Port | Path |
|---|---:|---:|---|
| Text Workstation | 1.8 stable | 8501 | `text_workstation/app.py` |
| Master Dashboard | 2.7 stable | 8502 | `master_dashboard/app.py` |
| Image Workstation | 3.x stable | 8503 | `image_workstation/app.py` |
| Voice Workstation | 4.x reference workflow | 8504 | `voice_workstation/app.py` |
| Video Workstation | 5.3 stable | 8505 | `video_workstation/app.py` |
| Portrait Workstation | 6.3 stable | 8506 | `portrait_workstation/app.py` |

## Recommended launcher

Use the all-in-one Colab launcher:

```text
launchers/all_in_one_colab_launcher.md
```

Supported `WORKSTATION` values:

```text
text
dashboard
image
voice
video
portrait
```

Example:

```bash
WORKSTATION="dashboard"
```

## Project workflows

Workflow documentation and templates live in:

```text
project_workflows/
```

Current workflows:

- `true_noir_tales_workflow.md`
- `true_noir_tales_package_template.json`
- `toolflow_workflow.md`
- `toolflow_package_template.json`

## Bangla Quality Engine

Core Bangla quality rules live in:

```text
docs/bangla_quality_engine.md
shared/bangla_quality_engine.py
docs/voice_video_bangla_quality.md
voice_workstation/bangla_voice_quality.py
video_workstation/bangla_video_quality.py
```

## Main Google Drive folders

Base path:

```text
/content/drive/MyDrive/NazLab
```

Important folders:

```text
chat_outputs
text_outputs
script_outputs
image_prompts
image_jobs
image_outputs
voice_outputs
voice_packages
voice_references
audio_outputs
video_outputs
video_packages
video_storyboards
portrait_packages
portrait_outputs
portrait_references
logs
config
```

## Workstation purposes

### Text Workstation

General Chat, Free Writer, Re-writer, Story Writer, Viral Script Writer, Caption Writer, Prompt Improver, Output Library, Settings, and Direct Test.

### Master Dashboard

Full-stack status, quick links, output folders, job queue, launcher notes, roadmap, and Bangla-first policy.

### Image Workstation

Image job builder, project presets, Bangladesh scenario policy, no-sindoor default rule, visual prompt package, and manual generator bridge.

### Voice Workstation

Narration direction, TTS direction, script draft, reference audio workflow, package JSON, and future audio backend metadata.

Reference voice/audio workflows must use user-provided or explicitly authorized reference audio only.

### Video Workstation

Video hook, subtitles, scene sequence, timing guide, shot list, editor instruction, storyboard save, and video package JSON.

### Portrait Workstation

Portrait prompt packages, reference image path support, output path validation, positive/negative prompt, and portrait package library.

Face references must be user-provided for the workflow.

## Visual safety defaults

General Naz Lab image/portrait prompts should use Bangladeshi people and scenarios by default.

Rules:

- urban and rural Bangladesh both supported
- women should have no sindoor unless explicitly requested
- no gore
- no blood-focused visuals
- no dead body
- no visible wounds
- no exposed violence
- adult-only for true-crime/noir content

## Backend status

Current workstations mostly create planning packages and metadata.

Text generation uses Ollama when running Text Workstation.

Future backend integrations can include:

- image generation backend
- TTS backend
- authorized reference voice backend
- video generation/editing backend
- portrait/reference workflow backend

## Current next steps

Recommended build order:

1. Keep Bangla Quality Engine aligned across all workstations.
2. Improve project workflow automation for True Noir Tales.
3. Improve project workflow automation for ToolFlow.
4. Build a dedicated workflow app/tab for one-topic-to-full-package generation.
5. Add safer reference managers where needed.
