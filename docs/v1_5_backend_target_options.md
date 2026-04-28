# Naz Lab v1.5 Backend Target Options

Status: decision prep  
Backend next phase: frozen until real trials complete  
Video generation: locked/deferred after v1

## Rule

Do not start backend v1.5 implementation until:

1. ToolFlow Dashboard verification passes.
2. ToolFlow PASS marker exists.
3. Real Content Package Trials COMPLETE marker exists.
4. User chooses one next target.

## Option 1 — Real image backend

Purpose:

- Turn image prompt packages into real generated image outputs.

Pros:

- Most directly useful for Facebook/Reel/social content.
- Lower complexity than real video generation.
- Fits current image prompt package structure.

Risks:

- Needs model/runtime decision.
- Needs safety and reference-face handling.
- Colab GPU availability may vary.

Good first target if the priority is visual output.

## Option 2 — FFmpeg assembly

Purpose:

- Assemble existing images, text, audio, and manifests into lightweight video files.

Pros:

- Avoids heavy AI video generation.
- Practical for final Reel packaging.
- Can run with CPU if assets already exist.

Risks:

- Needs reliable asset availability.
- Quality depends on input images/audio.
- Not image-to-video generation.

Good first target if the priority is real MP4 output without heavy AI generation.

## Option 3 — Real video generation groundwork

Purpose:

- Prepare future image-to-video or AI video backend architecture.

Pros:

- Sets up long-term video roadmap.
- Can define adapters, queues, manifests, runtime boundaries.

Risks:

- Highest complexity.
- GPU/runtime problems likely.
- Not recommended before image/audio/FFmpeg pipeline is stable.

Good only if the priority is architecture, not immediate output.

## Option 4 — Higher quality TTS

Purpose:

- Improve voiceover quality beyond generic placeholder TTS.

Pros:

- Useful for Reels and scripted packages.
- Less complex than full video generation.
- Can stay safe without cloning.

Risks:

- Voice model/runtime choice needed.
- Must avoid unauthorized voice cloning.
- Bangla quality varies by engine.

Good target if voiceover quality is the bottleneck.

## Option 5 — Local PC deployment support

Purpose:

- Make Naz Lab easier to run outside Colab.

Pros:

- Improves stability and ownership.
- Reduces Colab runtime friction.
- Useful before heavy backends.

Risks:

- Requires OS-specific instructions.
- User environment may vary.

Good target if reliability and repeatability matter more than new features.

## Recommended order after v1 completion

```text
1. FFmpeg assembly
2. Real image backend
3. Higher quality TTS
4. Local PC deployment support
5. Real video generation groundwork
```

This order produces practical output earlier while keeping real video generation deferred until the system is stable.
