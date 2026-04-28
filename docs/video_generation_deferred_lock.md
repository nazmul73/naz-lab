# Video Generation Deferred Lock

Status: locked
Date: 2026-04-28

## Decision

Real video generation is locked out of Naz Lab v1 practical-use completion.

## Meaning

Current v1 supports:

- video scene planning
- video manifest planning
- final reel package metadata
- placeholder video backend adapter
- Dashboard review of video plan packages

Current v1 does not support:

- rendered MP4 output
- real AI video generation
- image-to-video generation
- GPU video generation runtime

## Why locked

Real video generation is deferred because:

- current priority is content planning and packaging
- Colab runtime can be unstable for heavy models
- GPU availability is not guaranteed
- video tools need isolated runtime planning
- practical content workflows can be completed without real video generation

## Unlock conditions

Only unlock video generation after:

1. ToolFlow real content package trial passes.
2. Real Content Package Trials complete marker exists.
3. User explicitly requests video generation work.
4. A separate backend target is selected.
5. A runtime and dependency plan is created.

## Current marker

```text
Video generation — LOCKED / DEFERRED AFTER V1
Naz Lab v1 — PLANNING AND PACKAGING ONLY
```
