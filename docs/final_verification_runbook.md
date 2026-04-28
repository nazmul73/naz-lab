# Naz Lab Final Verification Runbook

Phase: Final Verification 1.0
Status: ready-for-final-test

## Purpose

This runbook is the final lightweight verification path for the current Naz Lab build.

It checks:

- latest repo state
- lightweight compile/import smoke test
- final reel pack assembler
- Dashboard Phase 2.14
- Final Packs tab
- Cloudflare openable public URL through the robust all-in-one launcher

This runbook does not run heavy generation tools.

## What this verifies

The current build should include:

- Text Workstation stable
- Master Dashboard Phase 2.14 with Final Packs tab
- Image Workstation stable
- Voice Workstation Phase 4.5 safer reference manager
- Video Workstation stable
- Portrait Workstation Phase 6.4 safer reference manager
- Project Workflow Workstation Phase 10.2
- Backend Adapter Skeletons 1.0
- Generic non-cloning TTS backend adapter
- Image placeholder backend adapter
- Video placeholder backend adapter
- Final reel pack assembler
- Robust all-in-one Colab launcher

## Cell 1 — mount Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

Expected result:

```text
Drive mounted or already mounted at /content/drive.
```

## Cell 2 — clone latest repo and run lightweight smoke test

```bash
%cd /content
!rm -rf naz-lab
!git clone https://github.com/nazmul73/naz-lab.git
%cd /content/naz-lab
!python backend_adapters/smoke_test_lightweight.py
```

Expected result:

```json
{
  "ok": true,
  "compile_total": 23,
  "import_total": 13,
  "failed": []
}
```

The exact totals may change when new files are added, but `ok` must be `true` and `failed` must be empty.

## Cell 3 — assemble final reel pack

```bash
!python backend_adapters/final_reel_pack_assembler.py --project "General" --title "final verification pack"
```

Expected result:

```json
{
  "ok": true,
  "status": "assembled",
  "json_path": "/content/drive/MyDrive/NazLab/final_reel_packs/...json",
  "markdown_path": "/content/drive/MyDrive/NazLab/final_reel_packs/...md"
}
```

Warnings are allowed if some output folders are empty, but the command should still produce JSON and Markdown files.

## Cell 4 — run Dashboard through robust all-in-one launcher

Open:

```text
launchers/all_in_one_colab_launcher.md
```

Use:

```bash
WORKSTATION="dashboard"
```

Expected result:

```text
NAZ LAB MASTER DASHBOARD READY
Open this URL:
https://something.trycloudflare.com
```

The launcher now uses `127.0.0.1` for Cloudflare origin handling and includes Streamlit health checks.

## Dashboard checks

Open the Cloudflare URL and confirm:

1. Dashboard shows Phase 2.14.
2. Status tab loads.
3. Backend Status tab loads.
4. Package Search tab loads.
5. Final Packs tab exists.
6. Latest final reel pack JSON is visible.
7. Download final pack JSON button appears.
8. Download final pack Markdown button appears.
9. Final pack preview shows warning count and source count.

## Pass condition

The current Naz Lab build passes final verification when:

```text
smoke_test_lightweight.py returns ok=true
final_reel_pack_assembler.py returns ok=true
Dashboard Phase 2.14 opens through a trycloudflare.com URL
Final Packs tab shows at least one JSON pack
```

## Failure handling

If Streamlit does not start:

```bash
!cat /content/streamlit_dashboard.log
```

If Cloudflare URL is not printed:

```bash
!cat /content/cloudflared_dashboard.log
```

If smoke test fails, copy the `failed` section from the JSON output.

## What is intentionally not verified here

This runbook does not verify:

- real Fooocus/SDXL image generation
- real FFmpeg rendered MP4
- XTTS/reference voice clone generation
- FaceFusion/LivePortrait generation
- production GPU backend runtime

Those belong to future real backend runbooks, one backend at a time.
