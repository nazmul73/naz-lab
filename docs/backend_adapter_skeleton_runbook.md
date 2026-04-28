# Naz Lab Backend Adapter Skeleton Runbook

Phase: Backend Adapter Skeletons 1.0
Status: lightweight-runbook-ready

## Purpose

This runbook explains how to use the lightweight backend adapter skeletons. These commands do not install or run heavy generation tools.

Use this runbook to:

- create backend package JSON from templates
- scan package/job readiness
- validate package JSON for future adapters
- mark package backend status safely

## Important rule

Do not use this runbook to run real generation yet.

Heavy tools such as Fooocus, Stable Diffusion, XTTS, LivePortrait, FaceFusion, FFmpeg-heavy video generation, or image-to-video models are not part of this skeleton runbook.

## Prerequisites

- Google Drive mounted in Colab
- Repo cloned at `/content/naz-lab`
- Naz Lab Drive folders initialized

## Setup command

From Colab:

```bash
%cd /content
!rm -rf naz-lab
!git clone https://github.com/nazmul73/naz-lab.git
%cd /content/naz-lab
```

Expected result:

```text
Repo is cloned and current working directory is /content/naz-lab.
```

## 1. Create backend package from template

Create a voice backend package:

```bash
!python backend_adapters/create_backend_package.py voice --project "General" --title "bangla voice test"
```

Expected result:

```json
{
  "ok": true,
  "path": "/content/drive/MyDrive/NazLab/job_queue/voice_jobs/backend_voice_general_bangla_voice_test_....json"
}
```

Create an image backend package:

```bash
!python backend_adapters/create_backend_package.py image --project "General" --title "bangla image test"
```

Create a video backend package:

```bash
!python backend_adapters/create_backend_package.py video --project "General" --title "bangla video test"
```

Create a portrait backend package:

```bash
!python backend_adapters/create_backend_package.py portrait --project "General" --title "bangla portrait test"
```

## 2. Scan backend queues

```bash
!python backend_adapters/scan_backend_queues.py
```

Expected result:

```text
A JSON report with summary fields:
- total
- ready
- blocked
- warning_only
```

This command checks package/job JSON readiness only.

## 3. Mark package ready for backend

Replace the path with a real package path created by the template command.

```bash
!python backend_adapters/mark_backend_status.py "/content/drive/MyDrive/NazLab/job_queue/voice_jobs/example.json" ready_for_backend "Ready for generic TTS backend" --allow-any-transition
```

Expected result:

```json
{
  "ok": true,
  "path": "...",
  "backend_status": "ready_for_backend",
  "backend_last_updated": "..."
}
```

## 4. Validate package using adapter skeleton

Voice/TTS validation:

```bash
!python backend_adapters/generic_tts_adapter.py "/content/drive/MyDrive/NazLab/job_queue/voice_jobs/example.json"
```

Image validation:

```bash
!python backend_adapters/image_adapter.py "/content/drive/MyDrive/NazLab/job_queue/image_jobs/example.json"
```

Video validation:

```bash
!python backend_adapters/video_adapter.py "/content/drive/MyDrive/NazLab/job_queue/video_jobs/example.json"
```

Portrait validation:

```bash
!python backend_adapters/portrait_adapter.py "/content/drive/MyDrive/NazLab/job_queue/face_jobs/example.json"
```

Expected result:

```text
A JSON plan showing:
- ok
- status
- messages
- warnings
- backend_kind
- adapter
- will_run_generation: false
- future_inputs
```

## Safety checks

The skeleton validators should block unsafe reference use.

Voice reference backend should require:

```text
reference_voice_authorized: true
```

Portrait reference backend should require:

```text
reference_image_authorized: true
no_misleading_identity_claim: true
```

## Dashboard check

Run Dashboard and open the Backend Status tab:

```bash
WORKSTATION="dashboard"
```

Expected result:

```text
Dashboard Phase 2.13 opens. Backend Status tab shows total, ready, blocked, warning-only counts.
```

## Next after skeleton runbook

After these skeleton commands are accepted, real backend implementation can start with one safe backend at a time.

Recommended first real backend candidates:

1. Generic TTS adapter.
2. Image prompt-to-output adapter.

Do not start multiple heavy backends at once.
