# Naz Lab FaceFusion Lab Colab Guide

This is a separate Colab notebook/runtime for FaceFusion. Do not run these commands inside the main dashboard notebook.

## Purpose

FaceFusion is planned for face swap, face enhancement, and face-related video workflows.

## Output folder

```text
/content/drive/MyDrive/NazLab/facefusion_outputs
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
!mkdir -p /content/drive/MyDrive/NazLab/facefusion_outputs
!mkdir -p /content/FaceFusionLab
```

## Cell 4: Install basics

```bash
!apt-get update -y
!apt-get install -y git curl ffmpeg
```

## Cell 5: Clone FaceFusion

```bash
%cd /content/FaceFusionLab
!git clone https://github.com/facefusion/facefusion.git
%cd /content/FaceFusionLab/facefusion
```

## Cell 6: Inspect official files

```bash
!ls -la
!find . -maxdepth 2 -type f | head -50
```

## Cell 7: Install FaceFusion

FaceFusion installation can change over time. Prefer the official installer if present.

```bash
%cd /content/FaceFusionLab/facefusion

if [ -f install.py ]; then
  python install.py --onnxruntime cuda
elif [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "No install.py or requirements.txt found. Check official FaceFusion docs."
fi
```

## Cell 8: Validate install

```bash
%cd /content/FaceFusionLab/facefusion
python facefusion.py --version || true
python facefusion.py run --help || true
```

## Cell 9: Run UI

```bash
%cd /content/FaceFusionLab/facefusion
python facefusion.py run --open-browser > /content/facefusion.log 2>&1 &
```

## Cell 10: Check logs

```bash
!cat /content/facefusion.log | tail -80
```

## Cell 11: Public link

Install tunnel if needed:

```bash
!npm install -g localtunnel
```

Try the likely UI port. If logs show a different port, replace 7860.

```bash
!npx localtunnel --port 7860
```

## Cell 12: Localtunnel password if needed

```bash
!curl ipv4.icanhazip.com
```

## Cell 13: Output check

```bash
!ls -lah /content/drive/MyDrive/NazLab/facefusion_outputs
```

## Troubleshooting

```bash
!nvidia-smi
!python --version
!pip list | grep -E "onnx|torch|cuda|gradio|facefusion" || true
!cat /content/facefusion.log | tail -120
```

## Notes

- Colab GPU/session limits can break heavy installs.
- Keep this notebook separate from the main dashboard.
- Save the public FaceFusion link in the main Naz Lab dashboard Video Tools tab.
