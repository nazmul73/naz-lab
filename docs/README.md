# Naz Lab Docs Index

This folder contains project-level guidance for Naz Lab.

## Current marker

```text
Naz Lab v1 — Runtime-tested practical-use system
Text Workstation Phase 1.10 — PASS
Dashboard Phase 2.17 — PASS
Dashboard Phase 2.18 — PASS
Dashboard Phase 2.19 — PASS
Unified Dashboard Phase 2.20 — repo-side complete; runtime test pending
Real Image Backend Phase 3.1 — PASS on Colab GPU
Final Content Package Flow 1-18 — repo-side complete; runtime test pending
Recommended CPU model — qwen2.5:1.5b
Emergency CPU fallback — qwen2.5:0.5b
GPU image backend — Diffusers / Stable Diffusion
Bangla Safe Mode — DEFAULT ON
Template-first Bangla output — READY
Image Job JSON queue handoff — READY
Shared Job Queue Schema — READY
Real Facebook posting — DISABLED / manual-gated
Video generation — Locked / Deferred after v1
```

## Official app map

```text
Text Workstation official path:
text_workstation/app_official.py

Text Workstation stable implementation:
text_workstation/app_phase110.py

Master Dashboard official path:
master_dashboard/app_official.py

Final Content Package Flow dashboard:
master_dashboard/app_phase222.py

Real Image Backend dashboard:
master_dashboard/app_phase221.py

Unified frontend dashboard:
master_dashboard/app_phase220.py

All-in-one Colab launcher:
launchers/naz_lab_all_in_one_colab.py
```

## Legacy app policy

```text
text_workstation/app.py — legacy fallback, kept for older launchers
master_dashboard/app.py — legacy fallback, kept for older dashboard search/package flows
app_official.py files — official generic entrypoints going forward
phase-specific app files — kept as direct test/fallback apps until final release archive decision
```

## Official structure cleanup status

```text
Priority 1 — Official structure cleanup: COMPLETE
README/current marker final update: DONE
Official app map: DONE
Old app.py policy: DONE
Old dashboard phase file policy: DONE
```

## Current completed scope

```text
Backend 1-20 — COMPLETE
Frontend 1-20 — COMPLETE repo-side
Phase 3.1 Real Image Backend — COMPLETE + Colab GPU PASS
Final Content Package Flow 1-18 — COMPLETE repo-side
```

## v1 practical-use rule

Naz Lab v1 supports practical content planning, image generation, packaging, preview, approval, and export.

Included now:

- topic input
- text/script package
- image prompt package
- image job queue
- real image generation on Colab GPU
- generated image metadata
- final content package builder
- manual prompt package mode
- reference image package mode
- package preview/approve/export
- Dashboard preview/search/export
- backend health/model health
- social review and manual-gated Facebook dry-run path

Not included now:

- real AI video generation
- rendered MP4 assembly
- image-to-video generation
- automatic Facebook posting without manual approval
- unauthorized voice/face cloning

## Runtime tests still pending

```text
Dashboard Phase 2.20 runtime test
Dashboard Phase 2.22 runtime test
master_dashboard/app_official.py runtime test
launchers/naz_lab_all_in_one_colab.py runtime test
Auto Package end-to-end runtime test
Manual Prompt Package runtime test
Reference Image Package runtime test
Final package export/approve runtime verification
```
