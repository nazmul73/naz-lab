# Naz Lab Docs Index

This folder contains project-level guidance for Naz Lab.

## Current marker

```text
Naz Lab v1.6 — Stable unified dashboard PASS
Naz Lab is now the primary dashboard and testing/control surface
Text Workstation controls — MERGED + PASS
Voice job/output workflow — MERGED + PASS
Image Workstation controls — MERGED + PASS
Contextual Review Package workflow — MERGED + PASS
Facebook Post / Social Gate controls — MERGED + PASS
No Complete Package tab — PASS
Main Hub runtime — PASS
Official wrapper runtime — PASS
All-in-one Colab launcher runtime — PASS
Real Image Backend Phase 3.1 — PASS on Colab GPU
Recommended CPU model — qwen2.5:1.5b
Emergency CPU fallback — qwen2.5:0.5b
GPU image backend — Diffusers / Stable Diffusion
Bangla Safe Mode — DEFAULT ON
Template-first Bangla output — READY
Image Job JSON queue handoff — READY
Shared Job Queue Schema — READY
Real Facebook posting — DISABLED / manual-gated
Video generation — Locked / Deferred
Real TTS engine — Pending connection
```

## Official app map

```text
Primary dashboard implementation:
master_dashboard/naz_lab_dashboard_v12.py

Official dashboard entrypoint:
master_dashboard/app_official.py

Stable wrapper path:
master_dashboard/app_main.py

Text panel inside Naz Lab:
master_dashboard/naz_lab_text_panel.py

Voice panel inside Naz Lab:
master_dashboard/naz_lab_voice_panel.py

Image panel inside Naz Lab:
master_dashboard/naz_lab_image_panel.py

Review package panel inside Naz Lab:
master_dashboard/naz_lab_review_panel.py

Facebook Post panel inside Naz Lab:
master_dashboard/naz_lab_facebook_panel.py

All-in-one Colab launcher:
launchers/naz_lab_all_in_one_colab.py
```

## Dashboard tabs

```text
Home
Text
Voice
Image
Video
Facebook Post
Files
Health / Logs
Runbook
```

## Runtime PASS markers

```text
docs/final_package_runtime_pass.md
Commit: 5602b853f00a20a2c815a5d8226aefd428e96593

docs/social_gate_dry_run_pass.md
Commit: 4dbd53b154475a5af07b93d3076f39780e873eee

docs/naz_lab_dashboard_v1_5_runtime_pass.md
Commit: 66976862098c27da94212b9baa011b7a060194f4

docs/naz_lab_dashboard_v1_6_stable_pass.md
Commit: 5b709e5e563f8d43c8a4d39c46445ad51566170d
```

## Legacy app policy

```text
text_workstation/app.py — legacy fallback, kept for older launchers
master_dashboard/app.py — legacy fallback, kept for older dashboard search/package flows
phase-specific dashboard apps — fallback backends only
Naz Lab dashboard — primary control/testing surface going forward
```

## Current completed scope

```text
Backend 1-20 — COMPLETE
Frontend 1-20 — COMPLETE
Main Hub runtime — PASS
Official wrapper runtime — PASS
All-in-one launcher runtime — PASS
Text controls inside Naz Lab — PASS
Voice job/output workflow inside Naz Lab — PASS
Image controls inside Naz Lab — PASS
Review package workflow inside Naz Lab — PASS
Facebook Post / Social Gate inside Naz Lab — PASS
Phase 3.1 Real Image Backend — COMPLETE + Colab GPU PASS
Package preview/approve/export — PASS
Social Gate dry-run / blocked-post logging — PASS
```

## v1.6 practical-use rule

Naz Lab v1.6 supports practical content planning, text generation, voice job management, image generation control, contextual review packages, preview, approval, export, and safe/manual-gated Facebook handoff from one dashboard.

Included now:

- topic input
- text/script/caption/prompt generation
- image prompt package
- image job queue
- image runtime checks
- real image generation control from the Image tab
- generated image gallery and metadata preview
- Drive-backed voice job JSON creation
- voice output viewer
- attach existing audio to voice job
- contextual review package builder inside Home
- manual/auto/reference package modes
- package preview/approve/export
- approved package handoff preview in Facebook Post
- safe Facebook config
- manual gate and social post log
- files/output browser
- health/log viewer

Not included now:

- real AI video generation
- rendered MP4 assembly
- image-to-video generation
- automatic Facebook posting without manual approval
- real TTS generation engine connection
- unauthorized voice/face cloning

## Remaining work

```text
Package-to-social-job bridge polish
Real TTS engine connection if final engine is selected
Final all-in-one launcher stable marker
MacBook/local control runbook
SageMaker migration plan
Video Workstation deferred until other tools are fully stable
```
