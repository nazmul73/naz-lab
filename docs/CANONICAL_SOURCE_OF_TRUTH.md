# Naz Lab Canonical Source of Truth

Date: 2026-04-29

This document defines the active source of truth for Naz Lab so future work does not drift between old plans, legacy launchers, and current dashboard code.

## Active runtime truth

The official dashboard entrypoint is:

```text
master_dashboard/app_official.py
```

Colab path:

```text
/content/naz-lab/master_dashboard/app_official.py
```

The root `app.py` is only a compatibility wrapper. It should not contain a separate workstation implementation.

## Active Colab launcher truth

The official notebook launcher is:

```text
launchers/naz_lab_official_colab_launcher.ipynb
```

The launcher should:

- mount Google Drive
- create Naz Lab Drive folders safely
- download latest `main`
- install lightweight requirements
- run Ollama helper with polling, not fixed sleep only
- validate key Python files with `py_compile`
- launch one Streamlit process on port `8502`

Legacy Markdown launchers may remain as documentation, but they are not the canonical Colab runtime path.

## Active dashboard truth

Normal Colab usage must run one Streamlit app/process only:

```text
python -m streamlit run /content/naz-lab/master_dashboard/app_official.py --server.port 8502
```

Do not run seven separate Streamlit workstation ports for normal Colab work.

## Active Text Builder truth

The official Text Builder panel is:

```text
master_dashboard/naz_lab_text_panel.py
```

The active generation backend is:

```text
shared.ollama_text_generation.call_ollama
```

The legacy file below is compatibility-only and must not be treated as the source of generation policy:

```text
text_workstation/app_phase110.py
```

The active model policy is:

```text
shared/model_policy.py
```

The active text generation policy is:

```text
shared/ollama_text_generation.py
```

## Active Drive path truth

Drive paths should be centralized through:

```text
shared/drive_paths.py
```

Important folders:

```text
/content/drive/MyDrive/NazLab/models/ollama
/content/drive/MyDrive/NazLab/chat_outputs
/content/drive/MyDrive/NazLab/text_outputs
/content/drive/MyDrive/NazLab/script_outputs
/content/drive/MyDrive/NazLab/image_prompts
/content/drive/MyDrive/NazLab/job_queue/image_jobs
/content/drive/MyDrive/NazLab/job_queue/voice_jobs
/content/drive/MyDrive/NazLab/job_queue/video_jobs
/content/drive/MyDrive/NazLab/image_outputs
/content/drive/MyDrive/NazLab/voice_outputs
/content/drive/MyDrive/NazLab/voice_outputs/reference_audio
/content/drive/MyDrive/NazLab/video_outputs
/content/drive/MyDrive/NazLab/social_review
/content/drive/MyDrive/NazLab/final_packages
/content/drive/MyDrive/NazLab/final_packages/exports
/content/drive/MyDrive/NazLab/reference_images
/content/drive/MyDrive/NazLab/logs
/content/drive/MyDrive/NazLab/config
```

## Active Voice policy truth

Reference audio policy lives at:

```text
voice_workstation/reference_audio_policy.md
```

The dashboard must enforce the consent text before saving or attaching reference audio:

```text
I confirm this reference audio is user-provided or explicitly authorized for this Naz Lab workflow.
```

## Current product constraints

- No standalone tab named `Complete Package` is used.
- Real video generation is deferred.
- Real Facebook posting remains disabled/manual-gated unless explicitly connected and approved.
- Heavy voice/image/video backend dependencies are optional and should not be added to the default lightweight Colab runtime unless that backend is enabled.

## Documentation precedence

Use this order when documents conflict:

1. `README.md`
2. `docs/CANONICAL_SOURCE_OF_TRUTH.md`
3. `CHANGELOG.md`
4. recent `docs/*_pass.md` markers
5. legacy plans and Markdown launchers

When a legacy plan conflicts with this document, this document and `README.md` win.
