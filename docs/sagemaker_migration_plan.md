# SageMaker Studio Lab Migration Plan

Date: 2026-04-29

Purpose: prepare Naz Lab for a later move from Colab-first runtime to Amazon SageMaker Studio Lab or a similar hosted notebook/runtime environment.

## Current runtime source of truth

```text
Primary dashboard: Naz Lab
Primary launcher: launchers/naz_lab_all_in_one_colab.py
Current storage: Google Drive mounted at /content/drive/MyDrive/NazLab
Current GPU image generation: Colab GPU + Diffusers
Video generation: deferred
Real Facebook posting: disabled/manual-gated
```

## Migration goal

```text
Keep the Naz Lab dashboard as the same control surface.
Move heavy or persistent runtime from Colab to SageMaker only after current tools are stable.
Keep file paths, model cache, outputs, and logs predictable.
```

## Migration phases

### Phase 1 — Environment inventory

```text
[ ] Python version check
[ ] Streamlit install check
[ ] requests/Pillow install check
[ ] torch/diffusers install check
[ ] GPU availability check
[ ] persistent storage availability check
[ ] GitHub pull/push access check
```

### Phase 2 — Path abstraction

```text
[ ] Add NAZLAB_BASE_PATH environment override
[ ] Keep Google Drive path as Colab default
[ ] Add SageMaker storage path option
[ ] Add local/MacBook path option
[ ] Make shared/drive_paths.py environment-aware
```

### Phase 3 — Model/cache migration

```text
[ ] Decide model cache folder
[ ] Move or re-download image model cache
[ ] Validate qwen/Ollama usage separately if needed
[ ] Keep heavy image/video cache outside Git
```

### Phase 4 — Dashboard launch

```text
[ ] Run master_dashboard/app_official.py
[ ] Confirm Naz Lab tabs
[ ] Confirm Text workflow
[ ] Confirm Voice job workflow
[ ] Confirm Image runtime status
[ ] Confirm Review workflow
[ ] Confirm Facebook Post safe config
```

### Phase 5 — GPU validation

```text
[ ] Run Image Runtime tab
[ ] Confirm torch/cuda/diffusers availability
[ ] Generate one selected image job
[ ] Validate image output and metadata
```

### Phase 6 — Documentation / cutover

```text
[ ] Add SageMaker launcher if needed
[ ] Add final SageMaker runbook
[ ] Mark SageMaker PASS only after actual runtime test
```

## Current decision

```text
Do not migrate now.
Keep Colab as the primary runtime until Naz Lab dashboard is stable and repeatedly verified.
Use this document as the migration checklist when ASL/SageMaker access is ready.
```

## Safety constraints

```text
Real Facebook posting remains disabled/manual-gated.
Video generation remains deferred.
No unauthorized voice/face cloning.
```
