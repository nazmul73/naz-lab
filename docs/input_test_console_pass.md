# Naz Lab Input Test Console Pass

Status: pass
Date: 2026-04-28

## Decision

The Naz Lab Input Test Console frontend is ready for v1 practical workflow testing.

## Verified by user

The following frontend workflows were tested through the Input Test Console:

- Full Content Package
- Text / Script
- Image Prompt
- Voice / TTS Plan
- Portrait Prompt
- Video Scene Plan
- Final Reel Pack Manifest

## Confirmed behavior

The Input Test Console can:

- accept topic/input from the frontend
- preview JSON output
- preview Markdown output
- save JSON packages to Drive
- use the clean default negative prompt
- create final reel pack manifest JSON
- integrate saved final packs with the Dashboard Final Packs tab
- show saved packages in Dashboard Package Search

## Clean negative prompt rule

Default negative prompt is:

```text
no fake logo, no watermark, no distorted face
```

This applies to:

- Image Prompt workflow
- Full Content Package image package
- Portrait Prompt workflow

## Dashboard verification

Dashboard checks passed:

- Final Packs tab shows the frontend final pack
- Final pack JSON count increased
- saved frontend final pack appears in the table
- selected pack dropdown works
- Package Search finds the saved final pack
- report export buttons are available
- selected package export buttons are available

## Video generation status

Real video generation remains deferred after v1.

The Video Scene Plan workflow creates planning/manifest output only.

## Current marker

```text
Input Test Console — PASS
Dashboard Final Packs integration — PASS
Dashboard Package Search integration — PASS
Naz Lab v1 practical testing frontend — READY
```

## Recommended next work

1. Mark the current frontend testing layer stable.
2. Use Input Test Console for real content package trials.
3. Polish generated Bangla quality where practical issues appear.
4. Defer real video generation to later dedicated sessions.
