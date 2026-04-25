# Naz Lab XTTS v2 Voice Lab Colab Guide

This is a planned separate Colab notebook/runtime for voice generation.

## Purpose

This lab is for permitted text-to-speech workflows and approved voice assets only.

## Output folder

```text
/content/drive/MyDrive/NazLab/voice_outputs
```

## Safety notice

Use only your own voice, licensed voice assets, or voices with clear permission. Do not imitate, impersonate, or mislead people.

## Status

Planned/later. Do not run this during the first main dashboard test.

## Cell 1: Mount Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## Cell 2: Check GPU

```bash
!nvidia-smi
```

## Cell 3: Create folders

```bash
!mkdir -p /content/drive/MyDrive/NazLab/voice_outputs
!mkdir -p /content/XTTSLab
```

## Cell 4: Install audio basics

```bash
!apt-get update -y
!apt-get install -y ffmpeg
```

## Cell 5: Install the official TTS package

Check the current official package documentation before running in production.

```bash
!pip install TTS
```

## Cell 6: Test import

```bash
!python -c "from TTS.api import TTS; print('TTS import OK')"
```

## Cell 7: Prepare a permitted text-to-speech test

```python
OUTPUT_PATH = "/content/drive/MyDrive/NazLab/voice_outputs/test_voice.wav"
TEXT = "এটি Naz Lab voice test।"
print("Use an official supported TTS model and authorized voice assets only.")
print("Output path:", OUTPUT_PATH)
```

## Cell 8: Output check

```bash
!ls -lah /content/drive/MyDrive/NazLab/voice_outputs
```

## Notes

- Keep the voice lab separate from the main dashboard.
- Save output paths or public links in the main Naz Lab dashboard Voice Tools tab.
- Do not use voices without consent.
