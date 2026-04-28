# Naz Lab v1 Finalization Plan

Phase: Naz Lab v1 Finalization
Status: active

## Decision

Naz Lab v1 will finalize the current non-heavy-generation content creation workflow first.

Real video generation is deferred to a later phase.

## Why video generation is deferred

Real video generation is the heaviest and riskiest part of the system because it may require:

- GPU runtime
- large model downloads
- FFmpeg/video assembly dependencies
- image-to-video model testing
- Colab runtime stability work
- storage and output size handling
- longer debug cycles

The current system can still be useful without real video generation because it already supports planning, prompts, voice/audio output, placeholder video manifests, and final reel pack assembly.

## v1 goal

Naz Lab v1 should be a stable Bangla-first content creation OS.

Core v1 flow:

```text
Topic / Idea
-> Project Workflow package
-> Text / script / caption package
-> Image prompt or placeholder output
-> Generic non-cloning TTS audio output
-> Video placeholder manifest
-> Final Reel Pack JSON/Markdown
-> Dashboard preview/download
```

## v1 included tools

### Text Workstation

Status: stable

Purpose:

- Bangla-first writing
- captions
- hooks
- scripts
- simple content package support

### Project Workflow Workstation

Status: stable

Purpose:

- one-topic-to-full-package workflow
- True Noir Tales package planning
- ToolFlow package planning
- General Bangla package planning

### Image Workstation

Status: stable

Purpose:

- image prompt generation
- image job package creation
- visual planning
- safe true-crime/noir prompt support

### Voice Workstation

Status: stable with safer reference manager

Purpose:

- generic voice planning
- authorized reference voice metadata
- non-cloning generic TTS backend path
- reference voice clone safety blocking

### Portrait Workstation

Status: stable with safer reference manager

Purpose:

- portrait prompt/package planning
- authorized reference image metadata
- reference image safety blocking

### Video Workstation

Status: planning/manifest stable

Purpose for v1:

- video scene planning
- reel planning
- video placeholder manifest

Not included in v1:

- real AI video generation
- rendered final MP4 generation

### Master Dashboard

Status: Phase 2.14

Purpose:

- workstation status
- links
- output folder status
- backend status
- package search
- final reel pack preview/download

### Backend adapters

Status: lightweight active

Included:

- generic non-cloning TTS adapter
- image placeholder adapter
- video placeholder adapter
- final reel pack assembler
- lightweight smoke test

Excluded from v1:

- real Fooocus/SDXL backend
- XTTS/reference voice clone backend
- FaceFusion/LivePortrait backend
- real video generation backend

## v1 pass criteria

Naz Lab v1 is ready when:

1. Lightweight smoke test passes.
2. Dashboard Phase 2.14 opens through robust launcher.
3. Final Packs tab shows generated final pack.
4. Package Search can export JSON/CSV/Markdown.
5. Backend Status tab loads.
6. Voice safer reference manager blocks unauthorized reference clone package.
7. Portrait safer reference manager blocks unauthorized reference image package.
8. Generic TTS backend can create MP3.
9. Image placeholder backend can create PNG placeholder.
10. Video placeholder backend can create manifest.
11. Final reel pack assembler creates JSON and Markdown.

## v1 final verification command set

Use:

```text
docs/final_verification_runbook.md
```

## Deferred video generation roadmap

Video generation moves to a later phase:

```text
Naz Lab v1.5 / v2 Video Generation
```

Future work:

1. FFmpeg assembly runbook.
2. Image-to-video backend selection.
3. GPU runtime test plan.
4. Real rendered MP4 output.
5. Dashboard video output preview/download.
6. Final Reel Pack MP4 inclusion.

## Current next work

1. Add video deferred roadmap note.
2. Add final verification status to docs.
3. Add Dashboard v1 readiness language.
4. Run final verification once.
5. After pass, mark Naz Lab v1 as ready.
