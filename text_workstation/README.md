# Naz Lab Text Workstation

Phase 1 of Naz Lab is the Text Workstation.

It is the writing and general-assistant center of the Naz Lab ecosystem.

## Features

- General Chat
- Story Writer
- Viral Script Writer
- Caption Writer
- Prompt Improver
- Output Library
- Settings
- Save Chat
- Save Output
- Prompt Improver to Image Job Queue

## Backend

- Streamlit frontend
- Ollama backend
- Default model: `gemma2:2b`
- Optional model: `mistral`

## Storage

Outputs are saved to Google Drive under `/content/drive/MyDrive/NazLab` using the shared path constants from `shared/drive_paths.py`.

## Public access

Cloudflare Tunnel is the primary public access method for Colab Streamlit apps.

Localtunnel is fallback only.

## Safety

Phase 1 does not install image, voice, video, or face-swap tools.
