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

### Changed

- Root `app.py` is now a thin wrapper that redirects to `master_dashboard/app_official.py`.
- README now identifies `master_dashboard/app_official.py` as the official runtime entrypoint.
- Text Builder now uses approved models only in the dashboard selector.
- Text Builder now saves metadata and Prompt Improver image jobs through the shared pipeline.
- Bangla generation token limits are increased through `shared/ollama_text_generation.py`.
- Gemma and Qwen prompt formatting are separated.
- Colab launcher now uses Ollama readiness polling instead of fixed sleep.

### Fixed

- Ollama Drive symlink/path race handling.
- Root app vs dashboard entrypoint confusion.
- Legacy multi-port dashboard guidance in README.
- Chat session loss for General Chat by adding incremental JSONL autosave.

### Documentation

- Added structural cleanup marker.
- Added code quality cleanup marker.
- Added conventional commit policy.
- Added Text Builder backend readiness marker.

## Notes

- Video generation remains deferred/planning-only.
- Real Facebook posting remains disabled/manual-gated.
- No standalone tab named Complete Package is used.
