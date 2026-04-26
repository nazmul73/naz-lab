# Naz Lab Shared Utilities

This folder contains lightweight helper code used by the Naz Lab modular workstation ecosystem.

## `drive_paths.py`

Defines the canonical Google Drive paths for the project:

- outputs
- job queues
- config files
- logs
- model persistence folders
- temp folder

All workstations should import these constants instead of hardcoding paths.

## `json_utils.py`

Provides safe JSON helpers for shared state files such as:

- `workstation_links.json`
- `output_log.json`
- `custom_gems.json`
- `tool_links.json`

The project can eventually run multiple Colab workstations. If two workstations write the same JSON file at the same time, the file can become corrupted. The safe write helpers reduce that risk by using:

1. lock files
2. temporary JSON writes
3. atomic replace
4. corrupted JSON backup
5. UTF-8 encoding

## Model persistence

Naz Lab uses `/content/drive/MyDrive/NazLab/models/ollama` as the persistent Ollama model folder. During setup, `/root/.ollama/models` is linked to that Drive folder.

This avoids re-downloading models every time Colab resets.

## Tunnel policy

Cloudflare Tunnel is the primary public access tool for future Streamlit apps.

Localtunnel is fallback only because it can produce Streamlit JavaScript module loading errors.

Ngrok is optional if the user has an auth token saved in Colab Secrets.
