# Naz Lab v1 Ready

Status: ready
Date: 2026-04-28

## Decision

Naz Lab v1 is ready as a Bangla-first content creation OS without real video generation.

Real video generation remains deferred to a later v1.5/v2 phase.

## Final verification evidence

Final verification confirmed:

- Dashboard Phase 2.14 loads.
- Final Packs tab exists.
- Final reel pack JSON files are visible.
- Final reel pack Markdown files are visible.
- Latest final verification pack is visible.
- Final pack JSON download button is available.
- Final pack Markdown download button is available.
- Final pack preview loads.
- Final pack status shows `assembled`.
- Warning count is 0 for the latest final verification pack.
- Source package count is visible.

## v1 included workflow

Naz Lab v1 supports:

```text
Topic / Idea
-> Project Workflow package
-> Text / script / caption package
-> Image prompt or placeholder output
-> Generic non-cloning TTS audio output
-> Video planning / placeholder manifest
-> Final Reel Pack JSON/Markdown
-> Dashboard preview/download
```

## v1 included tools

- Text Workstation
- Master Dashboard Phase 2.14
- Image Workstation
- Voice Workstation with safer reference manager
- Video Workstation planning/manifest flow
- Portrait Workstation with safer reference manager
- Project Workflow Workstation
- Backend Adapter Skeletons
- Generic non-cloning TTS backend adapter
- Image placeholder backend adapter
- Video placeholder backend adapter
- Final Reel Pack assembler
- Robust all-in-one Colab launcher
- Lightweight smoke test

## Deferred after v1

The following are not part of v1 and should be handled later:

- real AI video generation
- rendered final MP4 output
- FFmpeg video assembly
- image-to-video backend
- heavy GPU video runtime
- Fooocus/SDXL production backend
- XTTS/reference voice clone backend
- FaceFusion/LivePortrait production backend

## Next recommended work after v1

Recommended next work should happen one backend at a time:

1. Real image backend runbook, or
2. FFmpeg assembly runbook, or
3. TTS quality improvement path, or
4. Video generation v1.5 planning.

## Current marker

```text
Naz Lab v1 — Ready
Video generation — Deferred after v1
```
