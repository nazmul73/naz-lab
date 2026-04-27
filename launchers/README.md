# Naz Lab Launchers

This folder contains launcher instructions for running Naz Lab workstations in Google Colab.

## Recommended launcher

Use this first:

- `all_in_one_colab_launcher.md`

It can launch any workstation by changing one variable:

```bash
WORKSTATION="dashboard"
```

Supported values:

- `text`
- `dashboard`
- `image`
- `voice`
- `video`
- `portrait`

## Workstation ports

| Workstation | Port |
|---|---:|
| Text Workstation | 8501 |
| Master Dashboard | 8502 |
| Image Workstation | 8503 |
| Voice Workstation | 8504 |
| Video Workstation | 8505 |
| Portrait Workstation | 8506 |

## Current stack

- Text Workstation — Phase 1.8 stable
- Master Dashboard — Phase 2.7 stable
- Image Workstation — Phase 3.x stable
- Voice Workstation — Phase 4.x reference workflow
- Video Workstation — Phase 5.3 stable
- Portrait Workstation — Phase 6.3 stable

## Global content rule

Naz Lab is Bangla-first by default.

- Bangla first
- English second
- Other languages optional

Regional Bangla default: Rangpur / Nilphamari / North Bengal.

True Noir Tales and ToolFlow can remain English-first project presets when selected.
