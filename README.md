# Naz Lab AI Workstation

Naz Lab is a modular AI content production lab for Google Colab, Streamlit, Google Drive, Ollama, and future creative backends.

## Final status

Completion v1.1 aligns the repo with Working Plan v2.0 for the unified command center runtime.

Current official runtime:

```text
master_dashboard/app_official.py -> master_dashboard/app_main.py -> panel modules
```

`master_dashboard/naz_lab_dashboard_v12.py` remains as a compatibility dashboard hub and now routes to the same canonical panel functions.

## Quick Colab command

In a Google Colab Python cell, run:

```python
!wget -q -O /content/naz_lab_colab_run.py https://raw.githubusercontent.com/nazmul73/naz-lab/main/launchers/naz_lab_colab_run.py && python /content/naz_lab_colab_run.py
```

This downloads the permanent launcher, mounts Drive, downloads the latest `main` branch, installs minimal dashboard dependencies, validates key files, starts Streamlit on port `8502`, and opens the Colab proxy window.

For optional real GPU image generation dependencies, run this instead:

```python
!wget -q -O /content/naz_lab_colab_run.py https://raw.githubusercontent.com/nazmul73/naz-lab/main/launchers/naz_lab_colab_run.py && NAZLAB_INSTALL_IMAGE_DEPS=1 python /content/naz_lab_colab_run.py
```

## Official runtime entrypoint

Use one Streamlit process for normal Colab testing and production-style dashboard work:

```text
master_dashboard/app_official.py
```

Colab path:

```text
/content/naz-lab/master_dashboard/app_official.py
```

The root `app.py` is only a compatibility wrapper that redirects to the official dashboard.

## Official Colab launcher

Use either the quick command above or the notebook launcher:

```text
launchers/naz_lab_official_colab_launcher.ipynb
```

The notebook mounts Google Drive, prepares Naz Lab folders, downloads the latest `main` branch, installs requirements, validates all key dashboard/panel/backend modules, starts the official dashboard on port `8502`, and opens the Colab proxy window.

Legacy Markdown launchers may remain as documentation.

## Current vision

Naz Lab is now organized around a single dashboard command center:

```text
Idea / Topic
-> Text generation and metadata
-> Image prompt/job queue
-> Voice job workflow
-> Review / approve / export workflow
-> Facebook handoff
```

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

True Noir Tales and ToolFlow can remain English-first project presets when selected.

## Current dashboard stack

| Module | Status | Path |
|---|---|---|
| Official entrypoint | active | `master_dashboard/app_official.py` |
| Official dashboard hub | active | `master_dashboard/app_main.py` |
| Compatibility dashboard hub | active/compatibility | `master_dashboard/naz_lab_dashboard_v12.py` |
| Home panel | active | `master_dashboard/naz_lab_home_panel.py` |
| Text panel | active | `master_dashboard/naz_lab_text_panel.py` |
| Voice panel | active | `master_dashboard/naz_lab_voice_panel.py` |
| Image panel | active | `master_dashboard/naz_lab_image_panel.py` |
| Review panel | active | `master_dashboard/naz_lab_review_panel.py` |
| Facebook panel | active/manual-gated | `master_dashboard/naz_lab_facebook_panel.py` |
| Video panel | planning-only | `master_dashboard/naz_lab_video_panel.py` |
| Files panel | active | `master_dashboard/naz_lab_files_panel.py` |
| Health / Logs panel | active | `master_dashboard/naz_lab_health_panel.py` |
| Runbook panel | active | `master_dashboard/naz_lab_runbook_panel.py` |

Legacy workstation apps may exist as fallback modules, but normal Colab use should not run seven separate Streamlit apps or ports. Use the official dashboard on port `8502`.

## Main Google Drive folders

Base path:

```text
/content/drive/MyDrive/NazLab
```

Important folders:

```text
models/ollama
chat_outputs
text_outputs
script_outputs
image_prompts
job_queue/image_jobs
job_queue/voice_jobs
job_queue/video_jobs
image_outputs
voice_outputs
voice_outputs/reference_audio
video_outputs
social_review
final_packages
final_packages/exports
final_packages/drafts
reference_images
logs
config
```

## Text Builder backend policy

Recommended text models:

```text
gemma2:2b
qwen2.5:1.5b
qwen2.5:3b
```

Blocked for normal Text Builder Bangla generation:

```text
qwen2.5:0.5b
tinyllama
```

Text supports Generate, Save, Send to Image Job, Send to Voice Job, and Create Package Draft.

Prompt Improver generates metadata and queues image jobs under:

```text
/content/drive/MyDrive/NazLab/job_queue/image_jobs
```

## Image workflow

Image supports:

- direct Create Job from positive prompt
- default negative prompt: `no fake logo, no watermark, no distorted face`
- optional reference image upload
- queue inspection and schema validation
- manually controlled generation from queued jobs
- gallery and metadata preview

Real image generation requires the optional GPU/backend dependencies and a Colab GPU runtime. Job creation, validation, reference upload, gallery, and metadata remain available without GPU.

## Ollama persistence

Ollama model persistence uses:

```text
/content/drive/MyDrive/NazLab/models/ollama
```

The helper `shared/ollama_persistence.py` attempts to keep the local Ollama model path pointed at the Drive-backed model store and tolerates common Colab/Drive path race conditions.

## Workstation purposes

### Text

General Chat, Free Writer, Story Writer, Viral Script Writer, Caption Writer, Prompt Improver, YouTube Script, metadata save, image job handoff, voice job handoff, and package draft creation.

### Voice

Text-to-voice job planning, reference audio attachment, consent-gated reference audio upload, and voice output tracking.

Reference voice/audio workflows must use user-provided or explicitly authorized reference audio only.

### Image

Image job creation, reference upload, runtime checks, queue generation, gallery, metadata, and job validation.

### Review / export workflow

Contextual review, approve, and export flow through Home/Review areas.

### Facebook Post

Approved package handoff, safe config, manual gate, and social log. Real Facebook posting stays disabled/manual-gated unless explicitly connected and approved.

### Video

Video generation is deferred. The current section is planning-only until text, image, voice, and posting workflows are fully verified.

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

## Acceptance checklist

Use:

```text
docs/ACCEPTANCE_CHECKLIST.md
```

## Current next steps

Recommended build order:

1. Keep official Colab launcher passing.
2. Verify all 9 tabs open without crash.
3. Verify Text > Create, metadata, Prompt Improver job queue, Send to Voice Job, and Package Draft.
4. Verify Image > Create Job prompt form and queue preview.
5. Verify Voice attach-audio and Image reference upload UI.
6. Verify Facebook Post safe/manual config.
7. Add optional backend integrations only after dashboard workflow is stable.
