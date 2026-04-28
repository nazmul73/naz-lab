# Naz Lab Video Placeholder Backend Runbook

Phase: Video Placeholder Backend 1.0
Status: runbook-ready

## Purpose

This runbook defines the next safe backend target for Naz Lab: a video placeholder backend.

The first implementation should not install or run heavy video generation models. It should prove that a video package/job can move through backend validation, output path resolution, status updates, and Drive output saving.

## Current rule

Do not run heavy video generation in this phase.

This backend target should only support:

```text
Validated video package/job -> placeholder video manifest output
```

It should not install or run:

```text
image-to-video models
heavy FFmpeg pipelines
Runway/Pika/API video generation
ComfyUI video workflows
Face animation models
```

## Input package

Expected video package/job fields:

```json
{
  "backend_kind": "video",
  "backend_status": "ready_for_backend",
  "project_preset": "General",
  "platform": "Facebook Reels",
  "duration_seconds": 60,
  "scene_list": [],
  "image_paths": [],
  "voice_path": "",
  "caption": "",
  "video_output_path": "/content/drive/MyDrive/NazLab/video_outputs/example.mp4"
}
```

## Output target

Placeholder output should be saved to:

```text
/content/drive/MyDrive/NazLab/video_outputs
```

For this lightweight phase, the adapter may create a `.txt` manifest next to the future `.mp4` path instead of rendering actual video.

## Safety gates

Before output creation:

1. Validate package JSON.
2. Validate backend kind is `video`.
3. Validate project metadata is present.
4. Validate package status is `ready_for_backend` or allow draft only in manual test mode.
5. Save output only to Drive video output folder.
6. Do not claim a real final video was generated when only a placeholder manifest is created.

## Planned file

Implementation file:

```text
backend_adapters/video_placeholder_adapter.py
```

## Planned command

```bash
python backend_adapters/video_placeholder_adapter.py /content/drive/MyDrive/NazLab/job_queue/video_jobs/example.json
```

Expected result:

```json
{
  "ok": true,
  "status": "completed",
  "video_manifest_path": "/content/drive/MyDrive/NazLab/video_outputs/example.txt"
}
```

## Test package creation

Create a package from template:

```bash
python backend_adapters/create_backend_package.py video --project "General" --title "bangla video placeholder test"
```

Then mark ready:

```bash
python backend_adapters/mark_backend_status.py "PACKAGE_PATH" ready_for_backend "Ready for video placeholder backend" --allow-any-transition
```

Then run placeholder adapter:

```bash
python backend_adapters/video_placeholder_adapter.py "PACKAGE_PATH"
```

## Pass condition

The video placeholder backend phase passes when:

- video package JSON is created
- package is marked ready
- adapter validates package
- placeholder manifest is saved to Drive
- output log is updated
- backend status is marked completed
- Dashboard Backend Status shows updated status

## Next after pass

After video placeholder backend passes, choose one:

1. Final Reel Pack assembly planner.
2. Real image backend runbook.
3. Real video assembly runbook with FFmpeg.
4. Portrait placeholder backend.
