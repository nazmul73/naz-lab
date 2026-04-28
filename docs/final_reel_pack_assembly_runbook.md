# Naz Lab Final Reel Pack Assembly Runbook

Phase: Final Reel Pack Assembly 1.0
Status: runbook-ready

## Purpose

This runbook defines how Naz Lab should assemble a final content package after text, image, voice, and video placeholder/backend outputs exist.

This phase does not render a final video. It creates a final reel pack manifest that connects package metadata and saved output paths.

## Why this step matters

Naz Lab's original goal is a content creation workflow:

```text
Idea -> Text/Script -> Image -> Voice -> Video -> Final Reel Pack
```

The current backend phases have proven package-to-output steps for:

- generic TTS MP3 output
- image placeholder PNG output
- video placeholder manifest output

The final assembly manifest connects these outputs into one reusable package.

## Current rule

Do not run heavy rendering in this phase.

This backend target should only support:

```text
Package/output paths -> final reel pack manifest JSON + Markdown summary
```

It should not:

- render final MP4
- run FFmpeg
- call video generation APIs
- generate new images or audio
- bypass reference asset policy

## Input sources

A final reel pack may reference:

```text
/content/drive/MyDrive/NazLab/project_packages/*.json
/content/drive/MyDrive/NazLab/job_queue/image_jobs/*.json
/content/drive/MyDrive/NazLab/job_queue/voice_jobs/*.json
/content/drive/MyDrive/NazLab/job_queue/video_jobs/*.json
/content/drive/MyDrive/NazLab/image_outputs/*
/content/drive/MyDrive/NazLab/audio_outputs/*
/content/drive/MyDrive/NazLab/video_outputs/*
```

## Output target

Final reel pack manifests should be saved to:

```text
/content/drive/MyDrive/NazLab/final_reel_packs
```

Recommended output files:

```text
final_reel_pack_<project>_<title>_<timestamp>.json
final_reel_pack_<project>_<title>_<timestamp>.md
```

## Final reel pack fields

Recommended manifest fields:

```json
{
  "phase": "Final Reel Pack Assembly 1.0",
  "status": "assembled",
  "project_preset": "General",
  "title": "Example Reel",
  "language": "Bangla",
  "script_text": "...",
  "caption": "...",
  "hashtags": [],
  "image_paths": [],
  "audio_path": "...",
  "video_manifest_path": "...",
  "source_packages": [],
  "safety_notes": [],
  "created_at": "..."
}
```

## Safety gates

Before assembly:

1. Do not claim final rendered video exists unless MP4 output exists.
2. Preserve source package paths.
3. Preserve reference authorization metadata when present.
4. Preserve Bangla-first language metadata.
5. Mark missing output paths as warnings, not silent success.
6. Keep output as manifest/Markdown only in this phase.

## Planned file

Implementation file:

```text
backend_adapters/final_reel_pack_assembler.py
```

## Planned command

```bash
python backend_adapters/final_reel_pack_assembler.py --project "General" --title "bangla final reel test"
```

Expected result:

```json
{
  "ok": true,
  "status": "assembled",
  "json_path": "/content/drive/MyDrive/NazLab/final_reel_packs/final_reel_pack_general_....json",
  "markdown_path": "/content/drive/MyDrive/NazLab/final_reel_packs/final_reel_pack_general_....md"
}
```

## Pass condition

The final reel pack assembly phase passes when:

- final reel pack JSON is created
- final reel pack Markdown is created
- source package paths are recorded
- available image/audio/video output paths are recorded
- warnings are shown for missing outputs
- output log is updated

## Next after pass

After final reel pack assembly passes, choose one:

1. Add Dashboard final reel pack tab.
2. Add real image backend runbook.
3. Add real FFmpeg video assembly runbook.
4. Add production TTS quality improvement path.
