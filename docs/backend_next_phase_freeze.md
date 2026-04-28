# Backend Next Phase Freeze

Status: frozen-for-v1-practical-use
Date: 2026-04-28

## Decision

Backend heavy-generation work is frozen for the current v1 practical use milestone.

## Why

Naz Lab v1 has enough backend scaffolding and placeholder adapters to support practical content package planning, saving, and Dashboard review.

Real generation should not be mixed into the current validation flow because it can introduce heavy runtime issues, GPU dependency issues, model download complexity, and API/secret configuration issues.

## Frozen for v1

Do not start these during the current v1 practical-use finish:

- real video generation
- FFmpeg-rendered final MP4 assembly
- image-to-video backend
- GPU video runtime
- LivePortrait integration
- FaceFusion integration
- XTTS voice cloning
- Fooocus/Stable Diffusion heavy runtime integration

## Allowed in v1

Allowed:

- JSON package creation
- Input Test Console frontend trials
- Dashboard review/search/export
- generic non-cloning TTS path
- image prompt packaging
- video scene planning manifest
- placeholder backend adapters
- backend queue scanning

## Backend readiness already present

- backend schema helpers
- backend validation helpers
- backend queue helpers
- backend status helpers
- generic TTS adapter
- gTTS adapter
- image placeholder adapter
- video placeholder adapter
- final reel pack assembler
- lightweight smoke test

## Next phase entry criteria

Only begin backend next phase after:

1. ToolFlow real content package trial passes.
2. Real Content Package Trials complete marker exists.
3. User explicitly chooses next backend target.
4. Runtime requirements are planned separately.

## Possible next backend targets

Choose only one at a time:

1. Real image backend adapter.
2. FFmpeg assembly backend.
3. Real video generation groundwork.
4. Higher quality TTS backend.
5. Local PC deployment support.

## Current marker

```text
Backend next phase — FROZEN UNTIL REAL TRIALS COMPLETE
Naz Lab v1 backend — READY FOR PRACTICAL PACKAGE WORK
```
