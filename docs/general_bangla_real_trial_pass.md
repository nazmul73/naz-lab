# General Bangla Real Content Package Trial Pass

Status: pass
Date: 2026-04-28

## Decision

The General Bangla real content package trial passed.

Naz Lab v1 can generate and save a practical Bangla-first full content package from a real topic through the Input Test Console, then surface it through the Dashboard Package Search workflow.

## Trial input

### Input Test Console settings

```text
Project: General Bangla
Workflow to test: Full Content Package
Language: Bangla
Platform: Facebook Reel
Audience: Bangladeshi Facebook audience
```

### Topic

```text
AI tools দিয়ে ছোট ব্যবসার Facebook content বানানোর সহজ পদ্ধতি
```

### Direction / style

```text
সহজ মুখের বাংলা, বাস্তব ব্যবহারযোগ্য, ৬০ সেকেন্ডের Reel-ready package, ছোট ব্যবসায়ী audience, practical tone
```

## Verified behavior

The user verified:

- Input Test Console opens and runs.
- Full Content Package preview is generated.
- Package save works.
- Package is saved to Google Drive.
- Dashboard Phase 2.15 opens.
- Dashboard Package Search finds the saved General Bangla trial package.
- Selected package preview works.
- Download/export controls are available.

## Expected package sections

The saved package includes:

- text_package
- image_package
- voice_package
- video_plan
- posting_package
- safety_notes

## Current negative prompt rule

Default negative prompt remains:

```text
no fake logo, no watermark, no distorted face
```

## Video generation status

Real video generation remains deferred after v1.

The trial validates planning and packaging only, not rendered MP4 output.

## Current marker

```text
General Bangla real content package trial — PASS
Naz Lab v1 practical Bangla-first package flow — WORKING
```

## Recommended next work

1. Run True Noir Tales real package trial.
2. Run ToolFlow real package trial.
3. Polish output quality only where real use shows issues.
4. Keep real video generation deferred to a separate later phase.
