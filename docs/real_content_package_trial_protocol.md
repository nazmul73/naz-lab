# Naz Lab Real Content Package Trial Protocol

Status: active
Date: 2026-04-28

## Purpose

This protocol moves Naz Lab from build/testing mode into practical content package trial mode.

The goal is to test real creator use:

```text
real topic -> full package -> save -> dashboard review -> polish if needed
```

## Current system state

Naz Lab v1 is ready.

Verified layers:

- Input Test Console — PASS
- Dashboard Phase 2.15 — PASS
- Final Packs integration — PASS
- Package Search integration — PASS
- Video generation — deferred after v1

## Trial order

Recommended trial order:

1. General Bangla real package trial
2. True Noir Tales real package trial
3. ToolFlow real package trial

## Trial 1 — General Bangla

Use this first because it validates the core Bangla-first workflow.

### Input Test Console settings

```text
Project: General Bangla
Workflow to test: Full Content Package
Language: Bangla
Platform: Facebook Reel
Audience: Bangladeshi Facebook audience
```

### Trial topic

```text
AI tools দিয়ে ছোট ব্যবসার Facebook content বানানোর সহজ পদ্ধতি
```

### Direction / style

```text
সহজ মুখের বাংলা, বাস্তব ব্যবহারযোগ্য, ৬০ সেকেন্ডের Reel-ready package, ছোট ব্যবসায়ী audience, practical tone
```

### Expected package sections

The preview should include:

- text_package
- image_package
- voice_package
- video_plan
- posting_package
- safety_notes

### Quality checks

Check the output for:

- natural Bangla
- clear hook
- voiceover-ready lines
- useful caption
- clear CTA
- image prompt with Bangladeshi context
- clean negative prompt only
- generic/non-cloning voice plan
- video plan marked deferred after v1

### Clean negative prompt rule

Expected negative prompt:

```text
no fake logo, no watermark, no distorted face
```

### Save requirement

Click:

```text
Save JSON package
```

Expected folder:

```text
/content/drive/MyDrive/NazLab/project_packages/
```

## Dashboard review

After saving, open Dashboard Phase 2.15.

Check:

1. Final Packs, if a final pack manifest was saved.
2. Package Search.
3. Search keyword:

```text
AI tools
```

or:

```text
frontend_full_package
```

Expected:

- saved package appears
- selected package preview opens
- JSON download works
- Markdown download works
- report export works

## Pass criteria

Trial passes if:

- package preview is generated
- package saves to Drive
- Dashboard Package Search can find it
- content is usable with minor or no editing
- Bangla is natural enough for Facebook/Reel use
- no real video generation is claimed

## Polish criteria

Only polish if real output shows problems such as:

- too much English mixing
- weak hook
- stiff Bangla
- caption not useful
- image prompt too generic
- voiceover lines too long
- video scenes unclear

## Trial 2 — True Noir Tales

Use after General Bangla passes.

Settings:

```text
Project: True Noir Tales
Workflow to test: Full Content Package
Language: English or Bangla depending on target post
Platform: Facebook Reel
Audience: Tier-1 true crime audience or Bangladeshi audience if Bangla selected
```

Safety:

- adult-only
- no gore
- no dead body
- no visible wounds
- no exposed violence
- no sensational detail

## Trial 3 — ToolFlow

Use after General Bangla passes.

Settings:

```text
Project: ToolFlow
Workflow to test: Full Content Package
Language: English or Bangla depending on target post
Platform: Facebook Post or Facebook Reel
Audience: Tier-1 productivity / AI tools audience
```

Quality:

- practical
- clean
- non-hype
- no fake income claim
- no unverified AI news

## Current marker

```text
Naz Lab Real Content Package Trial — active
Start with General Bangla
```
