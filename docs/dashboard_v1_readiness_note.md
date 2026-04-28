# Dashboard v1 Readiness Note

Phase: Dashboard v1 Readiness
Status: ready-for-final-verification

## Purpose

This note defines how the Master Dashboard should be interpreted during Naz Lab v1 final verification.

Dashboard Phase 2.14 is the v1 control center for the current content creation workflow.

## Dashboard v1 meaning

Naz Lab Dashboard v1 means:

```text
Control center for Bangla-first content creation packages, outputs, backend readiness, and final reel pack manifests.
```

It does not mean:

```text
A full real video generation dashboard.
```

Real video generation is deferred after v1.

## Current Dashboard v1 responsibilities

The Dashboard should support:

- workstation status overview
- Cloudflare/workstation link saving
- output folder counts
- job/package tables
- lightweight backend status scanning
- package search
- JSON/CSV/Markdown export
- final reel pack preview
- final reel pack JSON download
- final reel pack Markdown download
- roadmap visibility

## Final Packs tab role

The Final Packs tab is the main v1 completion surface.

It should show:

- final reel pack JSON files
- final reel pack Markdown files
- status
- warning count
- source package count
- image path count
- audio path
- video manifest path
- JSON download button
- Markdown download button

The tab must not claim that a final MP4 video was rendered.

## Backend Status tab role

The Backend Status tab should show lightweight package/job readiness.

It does not run:

- Fooocus
- Stable Diffusion
- XTTS
- FaceFusion
- LivePortrait
- image-to-video models
- FFmpeg rendering

It only scans and reports package status.

## Package Search tab role

Package Search should help find and export:

- project packages
- image jobs
- voice packages
- video packages
- portrait packages
- final reel packs

Expected exports:

- report JSON
- report CSV
- report Markdown
- selected package JSON
- selected package TXT
- selected package Markdown

## v1 readiness checklist

Dashboard v1 is ready when:

1. Phase 2.14 loads.
2. Status tab loads.
3. Backend Status tab loads.
4. Final Packs tab loads.
5. Package Search tab loads.
6. Latest final reel pack appears.
7. Final pack JSON download appears.
8. Final pack Markdown download appears.
9. No final MP4/render claim appears.
10. Video generation remains marked as deferred.

## After v1

After v1 final verification passes, future work can continue in separate sessions:

- real image backend runbook
- FFmpeg assembly runbook
- real video generation backend selection
- production video output integration

## Current status

```text
Dashboard Phase 2.14 is ready for Naz Lab v1 final verification.
```
