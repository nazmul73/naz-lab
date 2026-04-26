# Naz Lab Phase 0 Foundation Setup Runbook

This runbook prepares the Google Drive foundation for the Naz Lab modular AI workstation ecosystem.

Phase 0 does **not** install Ollama, does **not** pull `gemma2:2b`, and does **not** create the Phase 1 Text Workstation app.

## Cell 1: Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

Expected result:

```text
Mounted at /content/drive
```

## Cell 2: Clone the GitHub repository

```bash
%%bash
cd /content
rm -rf /content/naz-lab
git clone --depth 1 https://github.com/nazmul73/naz-lab.git /content/naz-lab
cd /content/naz-lab
ls -lah
```

## Cell 3: Run Phase 0 setup

```bash
%%bash
python /content/naz-lab/master_setup/init_drive_structure.py
```

Expected final result:

```text
PHASE 0 PASSED
```

## Cell 4: Validate generated folders and JSON files

```bash
%%bash
python /content/naz-lab/master_setup/init_drive_structure.py

test -d /content/drive/MyDrive/NazLab/text_outputs
test -d /content/drive/MyDrive/NazLab/chat_outputs
test -d /content/drive/MyDrive/NazLab/script_outputs
test -d /content/drive/MyDrive/NazLab/image_prompts
test -d /content/drive/MyDrive/NazLab/job_queue/image_jobs
test -d /content/drive/MyDrive/NazLab/job_queue/voice_jobs
test -d /content/drive/MyDrive/NazLab/job_queue/video_jobs
test -d /content/drive/MyDrive/NazLab/job_queue/face_jobs
test -d /content/drive/MyDrive/NazLab/models/ollama
test -d /content/drive/MyDrive/NazLab/temp
test -f /content/drive/MyDrive/NazLab/config/workstation_links.json
test -f /content/drive/MyDrive/NazLab/config/custom_gems.json
test -f /content/drive/MyDrive/NazLab/config/tool_links.json
test -f /content/drive/MyDrive/NazLab/logs/output_log.json

echo "Phase 0 validation checks passed."
```

## Cell 5: Confirm expected output

If the setup script prints this line, Phase 0 is ready:

```text
PHASE 0 PASSED
```

## Notes

- Use active Colab cells exactly as shown.
- Do not use exported `.py` notebook code where `%%bash` is commented out.
- Cloudflare Tunnel is the preferred public access tool for future Streamlit workstations.
- Localtunnel is fallback only because it can cause Streamlit JavaScript loading issues.
- Phase 1 Text Workstation begins only after Phase 0 passes.
