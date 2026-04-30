# Changelog

All notable Naz Lab changes will be documented here.

## Unreleased

### Added

- Official single-dashboard Colab launcher notebook: `launchers/naz_lab_official_colab_launcher.ipynb`.
- Drive-backed Ollama runtime helper with polling and model pull progress: `scripts/ollama_colab_runtime.py`.
- Model-specific Ollama generation helper: `shared/ollama_text_generation.py`.
- Drive-backed chat autosave helper: `shared/chat_autosave.py`.
- Central Text Builder model policy: `shared/model_policy.py`.
- Backend smoke check helper: `scripts/backend_smoke_check.py`.
- Package `__init__.py` files for import stability.
- Completion v1.1 acceptance checklist: `docs/ACCEPTANCE_CHECKLIST.md`.
- Direct Image > Create Job prompt workflow with optional reference image upload.

### Changed

- Root `app.py` is now a thin wrapper that redirects to `master_dashboard/app_official.py`.
- README now identifies `master_dashboard/app_official.py` as the official runtime entrypoint.
- README now identifies `master_dashboard/app_main.py` as the official dashboard hub.
- `master_dashboard/naz_lab_dashboard_v12.py` now routes to canonical panel functions for compatibility.
- Text Builder now uses approved models only in the dashboard selector.
- Text Builder now saves metadata and Prompt Improver image jobs through the shared pipeline.
- Text Builder includes Send to Voice Job and Create Package Draft workflows.
- Bangla generation token limits are increased through `shared/ollama_text_generation.py`.
- Gemma and Qwen prompt formatting are separated.
- Colab launcher now uses Ollama readiness polling instead of fixed sleep.
- Colab launcher and smoke check now validate all Working Plan v2.0 panel modules.
- Tab label standardized to `Health / Logs`.

### Fixed

- Critical dashboard v12 function routing mismatch for Home, Video, Files, Health / Logs, and Runbook.
- Removed visible `MAIN MENU` and `SECTION MENU` headings from navigation.
- Ollama Drive symlink/path race handling.
- Root app vs dashboard entrypoint confusion.
- Legacy multi-port dashboard guidance in README.
- Chat session loss for General Chat by adding incremental JSONL autosave.
- Legacy `text_workstation/app_phase110.py` is not part of official validation.

### Documentation

- Added structural cleanup marker.
- Added code quality cleanup marker.
- Added conventional commit policy.
- Added Text Builder backend readiness marker.
- Added Working Plan v2.0 / Completion v1.1 runtime acceptance checklist.
- Updated README with final dashboard stack and Image Create Job workflow.

## Notes

- Video generation remains deferred/planning-only.
- Real Facebook posting remains disabled/manual-gated.
- No standalone tab named Complete Package is used.
