# Text Builder Backend Ready

Date: 2026-04-29

## Scope

This marker records backend-side readiness work before returning to Colab notebook testing.

## Completed backend work

- Central model policy added.
  - File: `shared/model_policy.py`
  - Allowed Text Builder models: `gemma2:2b`, `qwen2.5:1.5b`, `qwen2.5:3b`
  - Blocked weak Bangla models: `qwen2.5:0.5b`, `tinyllama`
- Text Builder panel hardened.
  - File: `master_dashboard/naz_lab_text_panel.py`
  - Model selector now uses the approved model policy.
  - Backend Status exposes allowed/blocked model policy.
  - Metadata sidecar and Prompt Improver auto image-job pipeline remain wired.
- Runtime dependencies updated.
  - File: `requirements.txt`
  - Added `Pillow` and `watchdog` alongside `streamlit` and `requests`.
- Backend smoke-check helper added.
  - File: `scripts/backend_smoke_check.py`
  - Validates Drive folders, OLLAMA_MODELS environment target, model policy import, optional Ollama binary visibility, and py_compile for key modules.
- Existing persistence and pipeline foundations remain active.
  - File: `shared/ollama_persistence.py`
  - File: `shared/text_pipeline.py`
  - File: `master_dashboard/app_official.py`

## Colab return plan

1. Download latest main branch.
2. Install requirements.
3. Optionally run `python /content/naz-lab/scripts/backend_smoke_check.py` after Drive mount.
4. Launch `/content/naz-lab/master_dashboard/app_official.py` on port 8502.
5. Test Text > Create.
6. Test casual chat: `how are you?`
7. Test Prompt Improver auto metadata and image job generation.
8. Check Text > Library > Text metadata.
9. Check Text > Library > Image jobs.
10. Check Text > Backend Status model policy and Ollama persistence.

## Expected policy

- `qwen2.5:0.5b` is no longer a normal selectable Text Builder model.
- Professional Bangla generation should use `gemma2:2b` or at least `qwen2.5:1.5b`.
- Prompt Improver jobs use the Drive-backed `job_queue/image_jobs` path through the dashboard pipeline.
- No standalone Complete Package tab is introduced.
