# Naz Lab Project Plan

## Phase 1: Main Dashboard + Text MVP

- Streamlit dashboard
- Ollama backend
- gemma2:2b default model
- optional Mistral model
- Default Naz Gems
- Output saving to Google Drive

## Phase 2: Custom Gems

- Create custom specialist agents from dashboard
- Save to custom_gems.json
- Load custom gems into Naz Gem dropdown
- Delete custom gems safely

## Phase 3: FaceFusion Lab

- Separate Colab notebook/runtime
- Install and test FaceFusion
- Save outputs to Google Drive
- Store public link/job plan in dashboard

## Phase 4: LivePortrait Lab

- Separate Colab notebook/runtime
- Install and test LivePortrait
- Save outputs to Google Drive
- Store public link/job plan in dashboard

## Phase 5: Fooocus Image Lab

- Separate Colab notebook/runtime
- Generate story scene images
- Save outputs to Google Drive
- Connect job plans from dashboard

## Phase 6: XTTS v2 Voice Lab

- Separate Colab notebook/runtime
- Text-to-speech workflow
- Authorized voice workflow only
- Save outputs to Google Drive

## Phase 7: Final Reel Pack Generator

- Package story, script, image prompts, voiceover text, video job plans, captions, and hashtags
- Export as text/JSON

## Phase 8: Full Workflow Orchestration

- Connect labs through Google Drive folders
- Dashboard as control center
- Keep heavy dependencies separated

## Core Rule

Do not install heavy tools inside the main dashboard. Keep FaceFusion, LivePortrait, Fooocus, and voice generation in separate Colab notebooks/runtimes.
