# MacBook / Local Control Runbook

Date: 2026-04-29

Purpose: prepare Naz Lab for local MacBook control while keeping Colab as the current primary runtime for GPU/image work.

## Current operating model

```text
Primary control surface: Naz Lab dashboard
Primary Colab launcher: launchers/naz_lab_all_in_one_colab.py
GPU image generation: Colab GPU
Drive storage: /content/drive/MyDrive/NazLab
Local MacBook role: controller/editor/planner until local runtime is fully configured
```

## Local MacBook target

```text
MacBook opens or edits repo
MacBook can run lightweight dashboard locally later
Heavy GPU image/video remains Colab/SageMaker
Drive/GitHub keep outputs and code synced
```

## Recommended local setup later

```bash
git clone https://github.com/nazmul73/naz-lab.git
cd naz-lab
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit requests pillow
python -m streamlit run master_dashboard/app_official.py --server.port 8502
```

## Local caveats

```text
Google Drive paths are currently Colab-style: /content/drive/MyDrive/NazLab
Local MacBook needs path mapping before full local file browsing works.
Ollama local model use can be added later.
GPU image generation should remain Colab/SageMaker unless a local GPU setup exists.
Facebook real posting remains disabled/manual-gated.
```

## Required future local path map

```text
Colab path:
/content/drive/MyDrive/NazLab

Mac path example:
/Users/<user>/Library/CloudStorage/GoogleDrive-<account>/My Drive/NazLab
```

## Priority tasks for local support

```text
[ ] Add environment variable NAZLAB_BASE_PATH override
[ ] Update shared/drive_paths.py to respect NAZLAB_BASE_PATH
[ ] Add local .env example
[ ] Add local launcher script
[ ] Add local health check for Ollama and Drive path
```

## Current status

```text
Runbook ready.
Local full runtime not yet the primary path.
Colab remains the source of truth for runtime tests.
```
