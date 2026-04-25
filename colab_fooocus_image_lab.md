# Naz Lab Fooocus Image Lab Colab Guide

This is a planned separate Colab notebook/runtime for Fooocus image generation.

## Purpose

Fooocus will generate images from story scene prompts.

## Output folder

```text
/content/drive/MyDrive/NazLab/image_outputs
```

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
!mkdir -p /content/drive/MyDrive/NazLab/image_outputs
!mkdir -p /content/FooocusLab
```

## Cell 4: Clone Fooocus

```bash
%cd /content/FooocusLab
!git clone https://github.com/lllyasviel/Fooocus.git
%cd /content/FooocusLab/Fooocus
```

## Cell 5: Install dependencies

Follow the official Fooocus README for current Colab installation. If requirements are present:

```bash
%cd /content/FooocusLab/Fooocus
!pip install -r requirements_versions.txt || pip install -r requirements.txt
```

## Cell 6: Run UI

```bash
%cd /content/FooocusLab/Fooocus
!python entry_with_update.py --share > /content/fooocus.log 2>&1 &
```

## Cell 7: Check logs

```bash
!cat /content/fooocus.log | tail -100
```

## Cell 8: Output check

```bash
!ls -lah /content/drive/MyDrive/NazLab/image_outputs
```

## Notes

- Keep Fooocus separate from the main dashboard.
- Save any public Fooocus link in the main Naz Lab dashboard Image Tools tab.
- Use this lab after the main dashboard, FaceFusion, and LivePortrait tests are stable.
