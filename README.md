# Naz Lab AI Workstation

Naz Lab is a modular AI content production lab for Google Colab, Streamlit, Google Drive, Ollama, and future creative backends.

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

Use the notebook launcher:

```text
launchers/naz_lab_official_colab_launcher.ipynb
```

This notebook mounts Google Drive, prepares Naz Lab folders, downloads the latest `main` branch, installs lightweight requirements, validates key modules, starts the official dashboard on port `8502`, and opens the Colab proxy window.

Legacy Markdown launchers may remain as documentation, but the notebook launcher is the recommended Colab path.

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

No standalone tab named Complete Package is used.

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
| Official Dashboard | active | `master_dashboard/app_official.py` |
| Dashboard implementation | active | `master_dashboard/naz_lab_dashboard_v12.py` |
| Text panel | active | `master_dashboard/naz_lab_text_panel.py` |
| Voice panel | active | `master_dashboard/naz_lab_voice_panel.py` |
| Image panel | active | `master_dashboard/naz_lab_image_panel.py` |
| Review panel | active | `master_dashboard/naz_lab_review_panel.py` |
| Facebook panel | active/manual-gated | `master_dashboard/naz_lab_facebook_panel.py` |

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

Prompt Improver generates metadata and queues image jobs under:

```text
/content/drive/MyDrive/NazLab/job_queue/image_jobs
```

## Ollama persistence

Ollama model persistence uses:

```text
/content/drive/MyDrive/NazLab/models/ollama
```

The helper `shared/ollama_persistence.py` attempts to keep the local Ollama model path pointed at the Drive-backed model store and tolerates common Colab/Drive path race conditions.

## Workstation purposes

### Text

General Chat, Free Writer, Story Writer, Viral Script Writer, Caption Writer, Prompt Improver, YouTube Script, metadata save, and image job handoff.

### Voice

Text-to-voice job planning, reference audio attachment, and voice output tracking.

Reference voice/audio workflows must use user-provided or explicitly authorized reference audio only.

### Image

Image job builder, reference upload, runtime checks, gallery, metadata, and job validation.

### Review / export workflow

Contextual review, approve, and export flow through Home/Review areas. No standalone Complete Package tab.

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

## Current next steps

Recommended build order:

1. Keep official Colab launcher passing.
2. Verify Text > Create, metadata, and Prompt Improver job queue.
3. Verify Voice attach-audio and Image reference upload UI.
4. Verify Facebook Post safe/manual config.
5. Add optional backend integrations only after dashboard workflow is stable.
