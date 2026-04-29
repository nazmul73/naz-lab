# Final All-in-One Launcher Stable Marker

Date: 2026-04-29

Status: repo-side stable marker ready. Runtime confirmation should be done after the next combined Naz Lab test.

## Official launcher

```text
launchers/naz_lab_all_in_one_colab.py
```

## Official app path

```text
master_dashboard/app_official.py
```

## Stable wrapper path

```text
master_dashboard/app_main.py
```

## Current dashboard implementation

```text
master_dashboard/naz_lab_dashboard_v12.py
```

## Current expected dashboard modules

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

## Current merged workflow expectation

```text
Text controls: inside Naz Lab
Voice job/output workflow: inside Naz Lab
Voice engine config: inside Naz Lab
Image controls: inside Naz Lab
Review package workflow: inside Home
Facebook Post controls: inside Naz Lab
Package-to-social-job bridge: inside Facebook Post
Video: deferred/locked
No Complete Package tab
```

## Stable launcher acceptance checklist

```text
All-in-one launcher starts without py_compile error
Naz Lab title visible
All tabs visible
Text Create works
Voice Runtime and Engine Config visible
Image Runtime and Generate visible
Home Review workflow visible
Facebook Approved Package / Safe Config / Manual Gate / Social Log visible
Files and Health tabs visible
No Complete Package tab
No Streamlit HTTP 500
```

## Policy

```text
Naz Lab dashboard is the primary testing/control surface.
Phase-specific apps remain fallback backends only.
```
