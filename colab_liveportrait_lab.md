# Naz Lab LivePortrait Lab Colab Guide

This is a separate Colab notebook/runtime for LivePortrait. Do not run these commands inside the main dashboard notebook.

## Purpose

LivePortrait is used to animate a static portrait image with a driving video or motion reference.

## Output folder

```text
/content/drive/MyDrive/NazLab/liveportrait_outputs
```

## Safety notice

Use only your own face, licensed assets, or people who gave clear permission. Do not impersonate real people or create misleading content.

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
!mkdir -p /content/drive/MyDrive/NazLab/liveportrait_outputs
!mkdir -p /content/LivePortraitLab
```

## Cell 4: Install basics

```bash
!apt-get update -y
!apt-get install -y git curl ffmpeg
```

## Cell 5: Clone LivePortrait

```bash
%cd /content/LivePortraitLab
!git clone https://github.com/KwaiVGI/LivePortrait.git
%cd /content/LivePortraitLab/LivePortrait
```

If the official repository changes, verify the current official LivePortrait repository before running.

## Cell 6: Install dependencies

```bash
%cd /content/LivePortraitLab/LivePortrait
!pip install -r requirements.txt
```

## Cell 7: Validate environment

```bash
!ffmpeg -version
!python -c "import torch; print('CUDA:', torch.cuda.is_available())"
!ls -la
```

## Cell 8: Prepare model weights

LivePortrait may require pretrained weights from the official project instructions. Follow the repository README for the latest weight download command.

If a download script exists:

```bash
%cd /content/LivePortraitLab/LivePortrait
!find . -maxdepth 3 -type f | grep -E "download|weight|model" || true
```

Run only the official download command from the repository README.

## Cell 9: Upload source and driving files

Upload your source portrait and driving video to Colab or Drive, then set paths:

```python
SOURCE_IMAGE = "/content/source.jpg"
DRIVING_VIDEO = "/content/driving.mp4"
OUTPUT_DIR = "/content/drive/MyDrive/NazLab/liveportrait_outputs"
```

## Cell 10: Run demo/test

The exact command can change by repository version. Inspect available inference scripts:

```bash
%cd /content/LivePortraitLab/LivePortrait
!find . -maxdepth 3 -type f | grep -E "inference|demo|app|gradio|run" || true
```

Use the official README command. A common pattern may look like this, but verify first:

```bash
# Example only - verify with README before running
# python inference.py --source /content/source.jpg --driving /content/driving.mp4 --output-dir /content/drive/MyDrive/NazLab/liveportrait_outputs
```

## Cell 11: Check outputs

```bash
!ls -lah /content/drive/MyDrive/NazLab/liveportrait_outputs
```

## Troubleshooting

```bash
!nvidia-smi
!ffmpeg -version
!python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
!pwd
!ls -la
```

## Notes

- Colab GPU/session limitations can affect model install and generation.
- Keep this notebook separate from the main dashboard.
- Save the public link or output path in the main Naz Lab dashboard Video Tools tab.
