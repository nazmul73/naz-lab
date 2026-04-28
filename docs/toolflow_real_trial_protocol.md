# ToolFlow Real Content Package Trial Protocol

Status: ready-for-user-test
Date: 2026-04-28

## Purpose

This protocol prepares the ToolFlow real content package trial.

The goal is to validate that Naz Lab v1 can create a practical, clean, non-hype AI tools/productivity package for a tier-1 audience.

## Current dependency state

Already passed:

- Input Test Console — PASS
- Dashboard Phase 2.16 deep package search — PASS
- General Bangla real trial — PASS
- True Noir Tales real trial — PASS

Pending user test:

- ToolFlow real package save
- Dashboard deep search verification
- ToolFlow real trial pass marker

## Input Test Console settings

Use:

```text
Project: ToolFlow
Workflow to test: Full Content Package
Language: English
Platform: Facebook Post
Audience: Tier-1 productivity / AI tools audience
```

## Trial topic

```text
How small business owners can use AI tools to plan one week of Facebook content in under 30 minutes
```

## Direction / style

```text
practical, clean, non-hype, beginner-friendly, no fake income claims, useful for small business owners, post-ready and reel-ready package
```

## Expected package sections

The package should include:

- text_package
- image_package
- voice_package
- video_plan
- posting_package
- safety_notes

## ToolFlow quality rules

The output should be:

- practical
- clear
- modern
- beginner-friendly
- non-hype
- no fake income claims
- no exaggerated promises
- useful for small business owners
- suitable for Facebook post and reel repurposing

## Image prompt expectations

Image package should be:

- productivity/SaaS style
- clean modern visual direction
- adult creator or business owner
- no fake logos
- no misleading software UI claims

Expected negative prompt:

```text
no fake logo, no watermark, no distorted face
```

## Video status

Real video generation remains deferred after v1.

Video output should be planning/manifest only.

Expected field:

```text
video_generation_status: deferred_after_v1
```

## Save requirement

Click:

```text
Save JSON package
```

Expected folder:

```text
/content/drive/MyDrive/NazLab/project_packages/
```

Expected filename pattern:

```text
frontend_full_package_toolflow_*.json
```

## Dashboard verification

Open Dashboard Phase 2.16 and go to:

```text
Package Search
```

Recommended search keywords:

```text
ToolFlow
```

```text
under 30 minutes
```

```text
small business owners
```

```text
frontend_full_package_toolflow
```

Expected:

- Matching packages count is greater than 0.
- Latest ToolFlow package appears.
- Selected package preview opens.
- Download selected JSON works.
- Download selected Markdown works.
- Report JSON/CSV/Markdown export buttons remain available.

## Pass criteria

ToolFlow trial passes only after the user verifies:

- package preview generated
- package saved to Drive
- Dashboard Phase 2.16 finds it
- package preview/download works
- content is practical and non-hype

## Marker to add after user verification

After user says the ToolFlow trial is saved and verified, add:

```text
ToolFlow Real Trial — PASS
```

## Current marker

```text
ToolFlow Real Trial — READY FOR USER TEST
```
