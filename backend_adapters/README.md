# Naz Lab Backend Adapters

Status: Backend Adapter Skeletons 1.0

This folder contains lightweight backend adapter entry points for future Naz Lab generation backends.

## Current rule

Do not install or run heavy generation tools from this folder yet.

The current backend adapter layer is only for:

- package/job scanning
- schema validation
- backend readiness checks
- reference asset policy checks
- future adapter planning

## Current files

- `scan_backend_queues.py` — scans package/job JSON folders and prints a validation report.

## Shared helper modules

- `shared/backend_schema.py` — backend status constants, kind inference, and default package shell.
- `shared/backend_validation.py` — required fields, status, output path, and reference policy validation.
- `shared/backend_queue.py` — scans backend queue/package folders.
- `shared/reference_asset_policy.py` — reference voice/image policy constants.

## Run command

From repo root:

```bash
python backend_adapters/scan_backend_queues.py
```

Expected result:

```text
A JSON report showing total packages, ready packages, blocked packages, warnings, and per-folder validation results.
```

## Backend adapter roadmap

Recommended order:

1. Keep lightweight scanner stable.
2. Add Dashboard backend status panel.
3. Add generic backend package status writer.
4. Add generic TTS adapter skeleton without heavy model install.
5. Add image adapter skeleton without heavy model install.
6. Add video and portrait adapter planning stubs.
7. Add real backend runbooks only when selected for testing.

## Safety requirement

Future adapters must block reference-based generation unless the package metadata confirms authorization:

- `reference_voice_authorized: true` for voice reference workflows
- `reference_image_authorized: true` for portrait/reference image workflows
- `no_misleading_identity_claim: true` for portrait/face workflows

## Bangla-first requirement

Backend outputs must preserve Naz Lab's Bangla-first direction:

- natural spoken Bangla
- Facebook-ready
- voiceover-ready
- simple and human
- default regional flavor: Rangpur / Nilphamari / North Bengal when appropriate
