# Naz Lab Docs Index

This folder contains project-level guidance for Naz Lab.

## Current marker

```text
Naz Lab v1 — Ready / Practical-use verified
Text Workstation Phase 1.10 — BACKEND + FRONTEND READY FOR COLAB/GPU TEST
Recommended CPU model — qwen2.5:1.5b
Emergency CPU fallback — qwen2.5:0.5b
Bangla Safe Mode — DEFAULT ON
Template-first Bangla output — READY
Image Job JSON queue handoff — READY
Shared Job Queue Schema — READY
Dashboard Phase 2.17 — QUEUE/TEXT/IMAGE VISIBILITY READY
Video generation — Locked / Deferred after v1
Real Content Package Trial — COMPLETE
Backend Next Phase — IN PROGRESS
```

## Active apps

```text
Text Workstation official stable app: text_workstation/app_phase110.py
Text Workstation legacy app: text_workstation/app.py
Master Dashboard queue visibility app: master_dashboard/app_phase217.py
Master Dashboard legacy app: master_dashboard/app.py
```

## Recent backend/frontend completion

- `docs/phase1_10_backend_frontend_ready.md` — Phase 1.10 backend/frontend readiness marker.
- `shared/job_queue_schema.py` — Shared queue schema, lifecycle statuses, validation, and image job helpers.
- `text_workstation/app_phase110.py` — Phase 1.10 Text Workstation app.
- `launchers/phase1_10_text_workstation_colab.py` — Phase 1.10 Colab launcher script.
- `master_dashboard/app_phase217.py` — Dashboard queue/text/image visibility app.

## Scope completed for requested items 1-10

```text
1. Phase 1.10 readiness marker — DONE
2. docs/README.md current marker update — DONE
3. app.py legacy handling decision — KEEP as legacy fallback until GPU test passes; app_phase110.py is official
4. Official Phase 1.10 launcher cleanup — DONE
5. Job Queue schema hardening — DONE
6. Image job status lifecycle standardize — DONE
7. Queue folders/status JSON validation — DONE
8. Master Dashboard queue visibility update — DONE via app_phase217.py
9. Dashboard Text Output browser update — DONE via app_phase217.py
10. Dashboard Image Job browser update — DONE via app_phase217.py
```

## v1 practical-use rule

Naz Lab v1 supports practical content planning and packaging, not real video generation.

Included now:

- topic input
- text/script package
- image prompt package
- generic voice/TTS plan package
- video planning manifest
- posting package
- package save to Drive
- Dashboard preview/search/export
- backend placeholder adapters and queue scanning
- queue visibility and validation

Not included now:

- real AI video generation
- rendered MP4 assembly
- image-to-video generation
- heavy GPU generation runtime
- unauthorized voice/face cloning

## Next pending work after Colab/GPU test

```text
11. Dashboard failed/approved job view
12. Image Workstation Bridge backend
13. Image jobs folder watcher
14. Image job pending → processing → done/failed status update
15. Image placeholder/adapter hook output path save
16. Social Review backend
17. Approved/rejected review status system
18. Social Review tab Dashboard integration
19. Approved jobs JSON flow
20. Backend status health summary JSON
```
