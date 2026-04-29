# Naz Lab Main Shell v1.1 Ready

Date: 2026-04-29

Status: repo-side shell update complete.

## User direction

```text
Main dashboard name: Naz Lab
The command center is not only a launcher map.
It should work like an app with a polished interface.
All workstations should connect behind this dashboard.
Video generation stays paused/deferred until other tools are ready.
No tab named Complete Package should be present.
```

## Implemented shell

Updated file:

```text
master_dashboard/app_main.py
```

Official entry remains:

```text
master_dashboard/app_official.py
```

Official launcher remains:

```text
launchers/naz_lab_all_in_one_colab.py
```

## Visible dashboard tabs

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

## Explicitly not included

```text
No tab named Complete Package
```

## Notes

- The visible title is now `Naz Lab`.
- The dashboard has an app-style command center shell.
- Text, voice, image, video, Facebook Post, files, health/logs, and runbook areas are represented.
- Video is clearly deferred/locked.
- Real Facebook posting remains disabled/manual-gated.
- Voice is represented in the shell but should not be marked runtime PASS until the actual voice backend is repo-integrated and Colab verified.
- Phase apps remain fallback backends while the unified dashboard matures.

## Next verification

Run the official all-in-one launcher or `master_dashboard/app_official.py` in Colab and verify:

```text
Naz Lab title visible
Home tab visible
Text tab visible
Voice tab visible
Image tab visible
Video tab visible and deferred
Facebook Post tab visible
Files tab visible
Health / Logs tab visible
Runbook tab visible
No Complete Package tab
No Streamlit crash / HTTP 500
```
