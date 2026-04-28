# Naz Lab Final Integration Checklist

Phase: Final Integration Polish 1.0
Status: checklist-ready

## Purpose

This checklist confirms that Naz Lab has moved from individual workstation builds into a connected Bangla-first content creation ecosystem.

It should be used before starting real backend adapter implementation for image, voice, video, or portrait generation.

## Core project goal

Naz Lab is a modular AI workstation ecosystem for content creation, especially Bangla content creation.

Primary content direction:

- Bangla-first content packages
- natural spoken Bangla
- Facebook-ready writing
- voiceover-ready scripts
- Rangpur / Nilphamari / North Bengal regional flavor when needed
- English support for True Noir Tales and ToolFlow when selected

## Current workstation status

| Workstation | Port | Current status | Final integration note |
|---|---:|---|---|
| Text Workstation | 8501 | Phase 1.8 stable | Writing and script foundation |
| Master Dashboard | 8502 | Phase 2.12 stable-package-export-buttons | Control center and package export |
| Image Workstation | 8503 | Phase 3.x stable | Image prompt/job planning |
| Voice Workstation | 8504 | Phase 4.5 clone-ready-safe-reference-manager | Safer reference voice planning |
| Video Workstation | 8505 | Phase 5.3 stable | Video/reel planning |
| Portrait Workstation | 8506 | Phase 6.4 stable-safe-reference-manager | Safer reference image planning |
| Project Workflow Workstation | 8507 | Phase 10.2 stable | One-topic-to-full-package planning |
| Reference Asset Policy | n/a | Phase 11.0 foundation ready | Shared safety policy constants/docs |
| Backend Planning | n/a | planning-ready | Heavy backend adapter strategy |

## Completed integration checks

### Dashboard

Expected:

- Phase 2.12 visible
- Drive base OK
- 7 workstations listed
- Package Search tab visible
- filtered report export buttons visible
- selected package export buttons visible

Export buttons expected:

- report JSON
- report CSV
- report Markdown
- selected package JSON
- selected package TXT
- selected package Markdown

Status: tested and passing.

### Portrait Workstation

Expected:

- Phase 6.4 visible
- safer reference manager visible
- upload/list/select reference image available
- authorization checkbox available
- reference notes available
- reference metadata preview available
- reference-based save blocks without reference image path and authorization

Observed expected block message:

```text
Cannot save reference-based portrait package: No reference image path provided yet.
```

Status: tested and passing.

### Voice Workstation

Expected:

- Phase 4.5 visible
- safer reference voice manager visible
- upload/list/select reference voice available
- authorization checkbox available
- reference notes available
- reference metadata preview available
- clone package save blocks without reference voice path and authorization

Observed expected block message:

```text
Cannot save clone package: No reference voice path provided yet.
```

Status: tested and passing.

## Colab one-click launch commands

Use the all-in-one launcher pattern from:

```text
launchers/all_in_one_colab_launcher.md
```

Supported workstation values:

```text
text
dashboard
image
voice
video
portrait
project
```

Recommended quick checks:

```bash
WORKSTATION="dashboard"
```

Expected result:

```text
Master Dashboard opens through a trycloudflare.com link and shows Phase 2.12.
```

```bash
WORKSTATION="portrait"
```

Expected result:

```text
Portrait Workstation opens through a trycloudflare.com link and shows Phase 6.4.
```

```bash
WORKSTATION="voice"
```

Expected result:

```text
Voice Workstation opens through a trycloudflare.com link and shows Phase 4.5.
```

## Safety gates

Before any real backend generation is connected, these gates must remain true:

### Voice reference gate

- reference audio must be user-provided or explicitly authorized
- allowed extensions only
- reference metadata must include authorization boolean
- backend must not use reference voice when authorization is false

### Portrait reference gate

- reference image must be user-provided or explicitly authorized
- allowed extensions only
- reference metadata must include authorization boolean
- no misleading identity claim
- backend must not use reference image as identity/face reference when authorization is false

### True Noir Tales visual gate

- adult-only subjects
- no gore
- no blood-focused visual
- no dead body
- no visible wounds
- no exposed violence
- restrained suspenseful tone

### Bangla quality gate

Bangla output must be:

- natural spoken Bangla
- simple and human
- Facebook-ready
- voiceover-ready
- not stiff textbook Bangla
- lightly regional when Rangpur/Nilphamari/North Bengal flavor is requested

## Package flow checklist

Use this flow for final package readiness:

1. Create topic in Project Workflow Workstation.
2. Generate full package plan.
3. Save package JSON to project packages.
4. Open Master Dashboard.
5. Search package in Package Search.
6. Preview package JSON.
7. Export package as JSON, TXT, or Markdown.
8. Use Image/Voice/Video/Portrait workstations for specialized package planning.
9. Save generated outputs to Drive folders when backend generation is added.
10. Final Reel Pack export is assembled from saved package and output paths.

## Backend adapter entry criteria

Do not start heavy backend adapter implementation until:

- Dashboard Phase 2.12 is confirmed working
- Voice Phase 4.5 safety gate is confirmed working
- Portrait Phase 6.4 safety gate is confirmed working
- backend planning doc is accepted
- one-click launcher works reliably enough for selected workstations
- package JSON structure is stable for the target backend

## Recommended next technical phase

After this checklist is accepted, the next technical phase should be:

```text
Backend Adapter Skeletons 1.0
```

Recommended order:

1. Shared backend adapter schema and status helpers.
2. Generic backend queue scanner.
3. Voice generic TTS adapter skeleton, no heavy model install yet.
4. Image backend adapter skeleton, no heavy model install yet.
5. Video/Portrait backend adapter planning stubs.
6. Dashboard backend status panel.

## No-test-needed note

This checklist document itself does not require a Colab runtime test.

Runtime tests are required only when code changes affect Streamlit apps, launchers, or backend execution.
