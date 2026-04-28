# Naz Lab Generic TTS Backend Runbook

Phase: Generic TTS Backend Runbook 1.0
Status: runbook-ready

## Purpose

This runbook defines the safest first real backend target for Naz Lab: generic TTS for Bangla-first narration output.

The goal is to generate simple narration audio from a validated voice package without using voice cloning or unauthorized reference audio.

## Why generic TTS first

Generic TTS is the safest first backend because:

- it does not require identity/voice cloning
- it can use script text from existing voice packages
- it supports the Bangla-first content creation goal
- it can save output directly to `audio_outputs`
- it does not need the Voice reference manager unless reference voice mode is selected

## Current rule

Do not run reference voice cloning in this phase.

This backend target should only support:

```text
Original / generic voice direction
Brand voice profile planning without cloning
Generic narration output
```

It should block:

```text
Authorized reference voice clone planning
```

unless a future dedicated reference-voice backend is intentionally selected and tested.

## Input package

Expected voice package/job fields:

```json
{
  "backend_kind": "voice",
  "backend_status": "ready_for_backend",
  "language": "Bangla",
  "voice_mode": "Original / generic voice direction",
  "tts_direction": "Natural spoken Bangla, clear pacing.",
  "script_draft": "Voiceover text here.",
  "audio_output_path": "/content/drive/MyDrive/NazLab/audio_outputs/example.mp3"
}
```

Fallback text fields may be accepted:

```text
script_draft
voiceover_text
text
combined_package
```

## Output target

Generated audio should be saved to:

```text
/content/drive/MyDrive/NazLab/audio_outputs
```

Optional metadata/log update:

```text
/content/drive/MyDrive/NazLab/logs/output_log.json
```

## Safety gates

Before generation:

1. Validate package JSON.
2. Validate backend kind is `voice`.
3. Validate status is `ready_for_backend` or allow draft only in manual test mode.
4. Validate script text is not empty.
5. Validate voice mode is not reference clone mode.
6. If `reference_voice_path` exists, require `reference_voice_authorized: true`, but still do not clone in this generic TTS phase.
7. Save output only to Drive audio output folder.

## Suggested first implementation strategy

Use a lightweight TTS adapter that can be replaced later.

Candidate options:

1. `gTTS` for quick internet-based generic TTS testing.
2. `edge-tts` for more voice options if network/runtime allows.
3. Future local/open-source TTS only after dependency testing.

Recommended first test:

```text
gTTS-based generic TTS adapter
```

Reason:

- simple install
- no GPU required
- no heavy model download
- good enough for proving package-to-audio pipeline

## Planned file

Future implementation file:

```text
backend_adapters/generic_tts_gtts_adapter.py
```

## Planned command

```bash
python backend_adapters/generic_tts_gtts_adapter.py /content/drive/MyDrive/NazLab/job_queue/voice_jobs/example.json
```

Expected result:

```json
{
  "ok": true,
  "audio_output_path": "/content/drive/MyDrive/NazLab/audio_outputs/example.mp3",
  "backend_status": "completed"
}
```

## Colab package install

Expected install command:

```bash
pip install -q gTTS
```

## Test package creation

Create a package from template:

```bash
python backend_adapters/create_backend_package.py voice --project "General" --title "bangla tts test"
```

Then edit package fields if needed:

```json
{
  "backend_status": "ready_for_backend",
  "script_draft": "আজ আমরা নাজ ল্যাবের বাংলা ভয়েস টেস্ট করছি।",
  "voice_mode": "Original / generic voice direction",
  "language": "Bangla"
}
```

## Expected limitations

- Voice may sound generic.
- Quality may not be final production quality.
- Bangla pronunciation depends on the selected TTS engine.
- Internet access may be required for gTTS.
- This does not clone any voice.

## Pass condition

The generic TTS backend phase passes when:

- a voice package JSON is created
- package is marked ready
- adapter validates package
- MP3 file is saved to Drive
- output log is updated
- backend status is marked completed
- Dashboard Backend Status shows updated status

## Next after pass

After generic TTS passes, choose one:

1. improve generic TTS quality
2. add image prompt-to-output backend runbook
3. add real image backend adapter
4. add production voice backend planning for better Bangla narration
