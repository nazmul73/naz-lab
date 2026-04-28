# Naz Lab Backend Adapters

Status: Backend Adapter Skeletons 1.0 + Generic TTS Adapter 1.0

This folder contains lightweight backend adapter entry points for future Naz Lab generation backends.

## Current rule

Do not install or run heavy generation tools from this folder yet.

The current backend adapter layer is for:

- package/job scanning
- schema validation
- backend readiness checks
- reference asset policy checks
- future adapter planning
- package backend status marking
- reusable backend package templates
- template-based backend package creation
- first generic non-cloning TTS audio generation

## Current files

- `scan_backend_queues.py` — scans package/job JSON folders and prints a validation report.
- `create_backend_package.py` — creates a backend package JSON from a reusable template.
- `mark_backend_status.py` — safely marks a package JSON as `ready_for_backend`, `blocked`, `failed`, `completed`, etc.
- `generic_tts_adapter.py` — validates a voice package and prints a future generic TTS execution plan.
- `generic_tts_gtts_adapter.py` — generates generic non-cloning MP3 audio from a validated voice package using gTTS.
- `image_adapter.py` — validates an image package/job and prints a future image generation plan.
- `video_adapter.py` — validates a video package and prints a future video/reel execution plan.
- `portrait_adapter.py` — validates a portrait package and prints a future portrait backend execution plan.

## Templates

Reusable package templates live in:

```text
backend_adapters/templates/
```

Current templates:

- `voice_backend_package_template.json`
- `image_backend_package_template.json`
- `video_backend_package_template.json`
- `portrait_backend_package_template.json`

## Shared helper modules

- `shared/backend_schema.py` — backend status constants, kind inference, and default package shell.
- `shared/backend_validation.py` — required fields, status, output path, and reference policy validation.
- `shared/backend_queue.py` — scans backend queue/package folders.
- `shared/backend_status.py` — safely marks package backend status with event history.
- `shared/reference_asset_policy.py` — reference voice/image policy constants.

## Run commands

From repo root:

```bash
python backend_adapters/scan_backend_queues.py
```

Expected result:

```text
A JSON report showing total packages, ready packages, blocked packages, warnings, and per-folder validation results.
```

Create a backend package from template:

```bash
python backend_adapters/create_backend_package.py voice --project "General" --title "bangla voice test"
```

Expected result:

```text
A JSON response showing ok=true and the created package path inside the relevant Drive job folder.
```

Mark a package ready for backend:

```bash
python backend_adapters/mark_backend_status.py /content/drive/MyDrive/NazLab/job_queue/voice_jobs/example.json ready_for_backend "Ready for generic TTS backend" --allow-any-transition
```

Expected result:

```text
A small JSON response showing ok=true, package path, backend_status, and backend_last_updated.
```

Validate a future voice/TTS package:

```bash
python backend_adapters/generic_tts_adapter.py /content/drive/MyDrive/NazLab/job_queue/voice_jobs/example.json
```

Generate generic non-cloning TTS audio:

```bash
python backend_adapters/generic_tts_gtts_adapter.py /content/drive/MyDrive/NazLab/job_queue/voice_jobs/example.json
```

Expected result:

```text
A JSON response showing ok=true, status=completed, and audio_output_path for the generated MP3.
```

Validate a future image package/job:

```bash
python backend_adapters/image_adapter.py /content/drive/MyDrive/NazLab/job_queue/image_jobs/example.json
```

Validate a future video package:

```bash
python backend_adapters/video_adapter.py /content/drive/MyDrive/NazLab/job_queue/video_jobs/example.json
```

Validate a future portrait package:

```bash
python backend_adapters/portrait_adapter.py /content/drive/MyDrive/NazLab/job_queue/face_jobs/example.json
```

## Backend adapter roadmap

Completed in Skeletons 1.0:

1. Lightweight scanner.
2. Dashboard backend status panel.
3. Generic backend package status writer.
4. Backend package status writer CLI.
5. Generic TTS adapter skeleton without heavy model install.
6. Image adapter skeleton without heavy model install.
7. Video and portrait adapter planning stubs.
8. Backend package templates.
9. Backend template creator/helper.
10. Generic gTTS backend adapter for non-cloning MP3 generation.

Recommended next:

1. Test generic gTTS adapter in Colab.
2. If test passes, choose either TTS quality improvement or image prompt-to-output backend.
3. Add real backend runbooks only when a real backend is selected for testing.

## Safety requirement

Future adapters must block reference-based generation unless the package metadata confirms authorization:

- `reference_voice_authorized: true` for voice reference workflows
- `reference_image_authorized: true` for portrait/reference image workflows
- `no_misleading_identity_claim: true` for portrait/face workflows

Generic gTTS adapter must not clone voices and must block reference clone mode.

## Bangla-first requirement

Backend outputs must preserve Naz Lab's Bangla-first direction:

- natural spoken Bangla
- Facebook-ready
- voiceover-ready
- simple and human
- default regional flavor: Rangpur / Nilphamari / North Bengal when appropriate
