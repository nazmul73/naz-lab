# Naz Lab Docs Index

This folder contains project-level guidance for Naz Lab.

## Core docs

- `bangla_quality_engine.md` — Global Bangla-first quality rules.
- `voice_video_bangla_quality.md` — Bangla quality rules for Voice and Video workflows.
- `reference_asset_policy.md` — Safe reference voice/face/portrait asset policy.
- `backend_planning.md` — Backend planning foundation for future heavy generation tools and adapters.

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

## Safety reminders

- Use adult-only subjects for true-crime/noir content.
- Avoid gore, dead bodies, visible wounds, and exposed violence.
- Use Bangladeshi people and scenarios by default for general Naz Lab visuals.
- Women should have no sindoor unless explicitly requested.
- Reference face/voice workflows require user-provided or explicitly authorized reference assets.

## Current build status

- Voice Workstation safer reference manager integration — done.
- Portrait Workstation safer reference manager integration — done.
- Dashboard Package Search download/export buttons — done.
- Backend planning foundation — done.

## Recommended next work

1. Test updated workstations in Colab.
2. Fix any runtime/UI issue from the tests.
3. Add backend adapter skeletons only after the planning doc is accepted.
4. Run final integration polish/checklist.
