# Naz Lab Video Generation Deferred Roadmap

Phase: Deferred Video Generation
Status: deferred-after-v1

## Decision

Real video generation is intentionally deferred until after Naz Lab v1 is finalized.

Naz Lab v1 will keep video workflow support through:

- video planning
- scene structure
- reel metadata
- video placeholder manifest
- final reel pack assembly

Naz Lab v1 will not include:

- real AI video generation
- rendered MP4 assembly
- GPU video model runtime

## Why defer video generation

Video generation has the highest runtime risk.

Expected risks:

- large model downloads
- GPU memory limitations
- Colab disconnects
- dependency conflicts
- slow rendering
- file size issues
- complicated debugging

Deferring video generation lets the rest of Naz Lab become stable and usable first.

## Current v1 video support

Current v1 support:

```text
Video package/job JSON
Video Workstation scene planning
Video placeholder backend manifest
Final Reel Pack video_manifest_path
Dashboard final pack preview/download
```

Current v1 output type:

```text
video placeholder manifest .txt
```

Not a final rendered video.

## Future v1.5/v2 video roadmap

### Stage 1 — FFmpeg assembly

Goal:

- assemble static images + audio + captions into MP4
- no AI video model required

Inputs:

- image outputs
- TTS audio
- caption text
- scene duration metadata

Outputs:

- MP4 file
- thumbnail
- assembly log

### Stage 2 — image-to-video backend

Goal:

- use selected image-to-video tool or API
- generate short clips from image prompts/output images

Requirements:

- selected backend
- GPU/API availability
- runtime test
- output folder policy

### Stage 3 — final video integration

Goal:

- include rendered MP4 in Final Reel Pack
- Dashboard preview/download support
- export-ready package for Facebook Reels

## Future backend candidates

Potential candidates, to be selected later:

- FFmpeg slideshow/reel assembly
- image-to-video Colab model
- external API-based video generation
- ComfyUI video workflow

No candidate is selected for v1.

## Safety gates for future video generation

Future video backend must preserve:

- adult-only true-crime/noir visuals
- no gore
- no dead body
- no visible wounds
- no exposed violence
- no unauthorized face/voice reference
- Bangla-first captions/voiceover
- final pack source traceability

## Resume condition

Video generation work should resume only after:

1. Naz Lab v1 final verification passes.
2. User confirms video generation is the next active priority.
3. One backend is selected for testing.
4. Colab/GPU/runtime requirements are accepted.

## Current status

```text
Deferred until after Naz Lab v1 finalization.
```
