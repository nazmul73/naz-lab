# Naz Lab Docs Index

This folder contains project-level guidance for Naz Lab.

## Core docs

- `bangla_quality_engine.md` — Global Bangla-first quality rules.
- `voice_video_bangla_quality.md` — Bangla quality rules for Voice and Video workflows.
- `reference_asset_policy.md` — Safe reference voice/face/portrait asset policy.

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

## Safety reminders

- Use adult-only subjects for true-crime/noir content.
- Avoid gore, dead bodies, visible wounds, and exposed violence.
- Use Bangladeshi people and scenarios by default for general Naz Lab visuals.
- Women should have no sindoor unless explicitly requested.
- Reference face/voice workflows require user-provided or explicitly authorized reference assets.

## Current next build order

1. Voice Workstation safer reference manager integration.
2. Portrait Workstation safer reference manager integration.
3. Download/export buttons for Dashboard Package Search.
4. Backend planning when ready.
