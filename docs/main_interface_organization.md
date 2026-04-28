# Main Interface Organization

Date: 2026-04-28

Status: COMPLETE

## Official main interface

```text
master_dashboard/app_official.py
```

The official dashboard wrapper points to the latest user workflow layer:

```text
master_dashboard/app_phase222.py
```

## Main dashboard app roles

```text
app_phase217.py — Queue, text output, image job visibility
app_phase218.py — Image Bridge, Social Review, Approved Flow
app_phase219.py — Model/Backend Health, Facebook config/manual gate
app_phase220.py — Unified frontend dashboard
app_phase221.py — Real Image Backend / Gallery / Job Preview
app_phase222.py — Final Content Package Flow
app_official.py — Official wrapper for current default interface
app.py — Legacy fallback
```

## Final main menu order

```text
1. Home / Status
2. Auto Package
3. Manual Prompt Package
4. Reference Image Package
5. Package Preview / Export
6. Approved Packages
7. Real Image Backend
8. Gallery
9. Jobs / Queue
10. Health
11. Facebook Gate
12. Checklist / Runbook
```

## Label policy

```text
Use user-facing labels:
- Ready
- Needs Action
- Runtime Pending
- Disabled by Design
- Manual Gate Required
- Legacy Fallback

Avoid internal-only labels in the main UI unless shown in debug/JSON views.
```

## Warning policy

```text
CUDA missing — show only in Real Image Backend runtime/generate views.
Facebook real posting — always show disabled/manual-gated unless explicitly configured.
Video generation — show deferred/locked after v1.
Legacy app warning — show only in runbook/status docs, not as blocking error.
```

## Status cards

```text
Text Workstation — Ready / PASS
Image Job Queue — Ready / PASS
Real Image Backend — GPU PASS, runtime depends on GPU availability
Final Content Package Flow — Repo-side Ready, runtime pending
Social Review — Ready / PASS
Facebook Gate — Disabled by Design / Manual Gate Required
Video Generation — Deferred
```

## Runtime dependency notes

```text
No GPU required:
- Final package schema
- Package builder
- Preview/export/approve
- Dashboard docs and package views

GPU required:
- Real image generation
- Manual prompt real image generation
- Reference image generation runtime test
```

## Completion

Priority 2 — Main interface organization is complete at the repo/docs level. Runtime testing remains separate.
