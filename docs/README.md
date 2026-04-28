# Naz Lab Docs Index

This folder contains project-level guidance for Naz Lab.

## Core docs

- `bangla_quality_engine.md` — Global Bangla-first quality rules.
- `voice_video_bangla_quality.md` — Bangla quality rules for Voice and Video workflows.
- `reference_asset_policy.md` — Safe reference voice/face/portrait asset policy.
- `backend_planning.md` — Backend planning foundation for future heavy generation tools and adapters.
- `final_integration_checklist.md` — Final integration readiness checklist before backend adapter skeletons.
- `backend_adapter_skeleton_runbook.md` — Lightweight backend skeleton command runbook.
- `generic_tts_backend_runbook.md` — First real backend target runbook for safe generic TTS.
- `image_prompt_backend_runbook.md` — Image prompt-to-output placeholder backend runbook.
- `video_placeholder_backend_runbook.md` — Video placeholder backend runbook.
- `final_reel_pack_assembly_runbook.md` — Final reel pack JSON/Markdown assembly runbook.
- `final_verification_runbook.md` — Final lightweight verification runbook for smoke test, final pack, and Dashboard Phase 2.14.
- `naz_lab_v1_finalization_plan.md` — Naz Lab v1 finalization scope with real video generation deferred.
- `video_generation_deferred_roadmap.md` — Future v1.5/v2 roadmap for real video generation.
- `../backend_adapters/README.md` — Backend Adapter Skeletons 1.0 overview and run commands.
- `../launchers/all_in_one_colab_launcher.md` — Robust one-click Colab launcher with Cloudflare public URL handling.

## Key language rules

Naz Lab is Bangla-first by default.

Bangla should be:

- natural spoken Bangla
- Facebook-ready
- netizen-friendly
- voiceover-ready
- subtitle-friendly when used in video
- simple and human
- not stiff textbook Bangla

Default regional flavor:

- Rangpur / Nilphamari / North Bengal

Secondary tones supported when requested:

- Dhakaiya
- Chattogram
- Sylhet
- Noakhali / Comilla

## Reference asset rules

Reference voice, face, or portrait assets must be:

- user-provided, or
- explicitly authorized for the workflow

Do not use reference assets for misleading, deceptive, unauthorized, or impersonation-style output.

Reference policy constants live in:

```text
shared/reference_asset_policy.py
```

## v1 finalization rule

Naz Lab v1 finalizes the current Bangla-first content creation workflow without real video generation.

Included in v1:

- text/script/caption workflows
- project workflow packages
- image prompt/package workflows
- generic non-cloning TTS audio path
- portrait/reference safety workflows
- video planning and placeholder manifest
- final reel pack JSON/Markdown assembly
- Dashboard preview/download/control center

Deferred after v1:

- real AI video generation
- FFmpeg-rendered final MP4
- image-to-video backend
- GPU video runtime

## Backend planning rules

Backend generation should stay separate from the Master Dashboard.

Heavy tools such as Fooocus, Stable Diffusion, XTTS, video generation tools, LivePortrait, and FaceFusion should run in isolated workstation runtimes or future backend adapters.

Backend adapters must validate:

- package/job JSON
- output folders
- allowed file extensions
- reference asset authorization metadata
- GPU/API/token requirements when relevant

Backend planning lives in:

```text
docs/backend_planning.md
```

Naz Lab v1 finalization plan lives in:

```text
docs/naz_lab_v1_finalization_plan.md
```

Video generation deferred roadmap lives in:

```text
docs/video_generation_deferred_roadmap.md
```

Final integration checklist lives in:

```text
docs/final_integration_checklist.md
```

Backend skeleton runbook lives in:

```text
docs/backend_adapter_skeleton_runbook.md
```

Generic TTS backend runbook lives in:

```text
docs/generic_tts_backend_runbook.md
```

Image prompt backend runbook lives in:

```text
docs/image_prompt_backend_runbook.md
```

Video placeholder backend runbook lives in:

```text
docs/video_placeholder_backend_runbook.md
```

Final reel pack assembly runbook lives in:

```text
docs/final_reel_pack_assembly_runbook.md
```

Final verification runbook lives in:

```text
docs/final_verification_runbook.md
```

Backend adapter skeletons live in:

```text
backend_adapters/
backend_adapters/templates/
shared/backend_schema.py
shared/backend_validation.py
shared/backend_queue.py
shared/backend_status.py
```

Robust Colab launcher lives in:

```text
launchers/all_in_one_colab_launcher.md
```

## Safety reminders

- Use adult-only subjects for true-crime/noir content.
- Avoid gore, dead bodies, visible wounds, and exposed violence.
- Use Bangladeshi people and scenarios by default for general Naz Lab visuals.
- Women should have no sindoor unless explicitly requested.
- Reference face/voice workflows require user-provided or explicitly authorized reference assets.
- Generic TTS backend must not perform voice cloning.
- Image placeholder backend must not claim to create final AI artwork.
- Video placeholder backend must not claim to create final rendered video.
- Final reel pack assembler must not claim to render final MP4.
- Real video generation is deferred until after Naz Lab v1 final verification passes.

## Current build status

- Voice Workstation safer reference manager integration — done and tested.
- Portrait Workstation safer reference manager integration — done and tested.
- Dashboard Package Search download/export buttons — done and tested.
- Backend planning foundation — done.
- Final integration checklist — done.
- Backend Adapter Skeletons 1.0 — done as lightweight skeleton, no heavy generation tools installed.
- Dashboard backend status panel — done.
- Backend skeleton command runbook — done.
- Generic TTS Backend Runbook 1.0 — done.
- Generic gTTS backend adapter — done and tested by user.
- Image Prompt Backend Runbook 1.0 — done.
- Image placeholder backend adapter — done and tested by user.
- Video Placeholder Backend Runbook 1.0 — done.
- Video placeholder backend adapter — done and tested by user.
- Final Reel Pack Assembly Runbook 1.0 — done.
- Final reel pack assembler — done and tested by user.
- Dashboard final reel pack tab — done.
- Robust all-in-one Colab launcher — done.
- Lightweight integration smoke test — done.
- Final verification runbook — done.
- Naz Lab v1 finalization plan — done.
- Video generation deferred roadmap — done.

## Recommended next work

1. Add Dashboard v1 readiness language if needed.
2. Run final verification runbook once in Colab.
3. If final verification passes, mark Naz Lab v1 ready.
4. Do real video generation later during separate work sessions.
