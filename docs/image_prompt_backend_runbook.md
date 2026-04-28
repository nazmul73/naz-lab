# Naz Lab Image Prompt-to-Output Backend Runbook

Phase: Image Prompt Backend Runbook 1.0
Status: runbook-ready

## Purpose

This runbook defines the second safe backend target for Naz Lab: an image prompt-to-output backend.

The first implementation should not install Fooocus, Stable Diffusion, SDXL, or any heavy image model. Instead, it should prove the package-to-output pipeline by creating a placeholder PNG from a validated image package/job.

## Why placeholder image backend first

A placeholder backend is useful because it verifies:

- image package/job JSON can be created
- package can be marked ready for backend
- backend adapter can validate package fields
- output path can be resolved safely
- output file can be saved to Drive
- backend status can be marked completed
- Dashboard Backend Status can show package status

This prevents heavy image model debugging from blocking the core package pipeline.

## Current rule

Do not run heavy image generation in this phase.

This backend target should only support:

```text
Validated image package/job -> placeholder PNG output
```

It should not install or run:

```text
Fooocus
Stable Diffusion
SDXL
ComfyUI
Automatic1111
API-based image generation
```

## Input package

Expected image package/job fields:

```json
{
  "backend_kind": "image",
  "backend_status": "ready_for_backend",
  "project_preset": "General",
  "positive_prompt": "Realistic cinematic Bangladeshi social image...",
  "negative_prompt": "no gore, no dead body...",
  "output_format": "1:1 square",
  "image_output_path": "/content/drive/MyDrive/NazLab/image_outputs/example.png"
}
```

Fallback prompt fields may be accepted:

```text
positive_prompt
prompt
combined_prompt
```

## Output target

Generated placeholder image should be saved to:

```text
/content/drive/MyDrive/NazLab/image_outputs
```

Optional metadata/log update:

```text
/content/drive/MyDrive/NazLab/logs/output_log.json
```

## Safety gates

Before output creation:

1. Validate package JSON.
2. Validate backend kind is `image`.
3. Validate package has prompt text.
4. Validate package status is `ready_for_backend` or allow draft only in manual test mode.
5. Preserve safety text such as adult-only/no-gore/no-visible-wounds when present.
6. Save output only to Drive image output folder.

## Planned file

Implementation file:

```text
backend_adapters/image_placeholder_adapter.py
```

## Planned command

```bash
python backend_adapters/image_placeholder_adapter.py /content/drive/MyDrive/NazLab/job_queue/image_jobs/example.json
```

Expected result:

```json
{
  "ok": true,
  "status": "completed",
  "image_output_path": "/content/drive/MyDrive/NazLab/image_outputs/example.png"
}
```

## Test package creation

Create a package from template:

```bash
python backend_adapters/create_backend_package.py image --project "General" --title "bangla image test"
```

Then mark ready:

```bash
python backend_adapters/mark_backend_status.py "PACKAGE_PATH" ready_for_backend "Ready for image placeholder backend" --allow-any-transition
```

Then run placeholder adapter:

```bash
python backend_adapters/image_placeholder_adapter.py "PACKAGE_PATH"
```

## Expected limitations

- This does not generate real AI artwork.
- The PNG is only a placeholder with package metadata/prompt summary.
- This phase is for pipeline validation only.

## Pass condition

The image prompt backend phase passes when:

- image package JSON is created
- package is marked ready
- adapter validates package
- PNG placeholder is saved to Drive
- output log is updated
- backend status is marked completed
- Dashboard Backend Status shows updated status

## Next after pass

After placeholder image backend passes, choose one:

1. Add real image backend runbook.
2. Add image backend adapter for a selected engine.
3. Improve Dashboard final reel package assembly.
4. Continue with video assembly placeholder backend.
