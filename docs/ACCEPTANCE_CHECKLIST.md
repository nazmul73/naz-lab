# Naz Lab Acceptance Checklist

Working Plan v2.0 / Completion v1.1 acceptance checklist.

## Runtime

- [ ] Official entrypoint launches: `master_dashboard/app_official.py`.
- [ ] Dashboard opens in Colab on port `8502`.
- [ ] 9 tabs are visible: Home, Text, Voice, Image, Video, Facebook Post, Files, Health / Logs, Runbook.
- [ ] No tab named `Complete Package` exists.
- [ ] Main menu and section menu labels are not shown as extra headings.

## Text

- [ ] Text > Create opens.
- [ ] Generate works or safely falls back.
- [ ] Save current output works.
- [ ] Send to Image Job works.
- [ ] Send to Voice Job works.
- [ ] Create Package Draft works.
- [ ] Backend Status shows `shared.ollama_text_generation.call_ollama`.
- [ ] Backend Status shows `shared.text_workstation_helpers`.
- [ ] Backend Status shows `legacy_app_phase110_active = False`.

## Image

- [ ] Image > Create Job opens.
- [ ] Positive prompt input is visible.
- [ ] Negative prompt defaults to `no fake logo, no watermark, no distorted face`.
- [ ] Optional reference image upload is visible.
- [ ] Create Image Job writes JSON under `/content/drive/MyDrive/NazLab/job_queue/image_jobs`.
- [ ] Image > Job Preview validates the created job.
- [ ] Image > Generate remains manual/GPU-gated.
- [ ] Image > Gallery and Metadata open without crashing.

## Voice

- [ ] Voice > Create Job opens.
- [ ] Voice job JSON is created.
- [ ] Attach Audio opens.
- [ ] Reference audio consent gate is required before saving/attaching reference audio.
- [ ] Voice outputs preview with `st.audio` when audio exists.

## Facebook Post

- [ ] Targets / Safe Config opens.
- [ ] Manual Gate opens.
- [ ] Dry-run/manual-gated flow is visible.
- [ ] Real posting remains disabled by default.
- [ ] Missing token/target blocks safely.

## Video

- [ ] Video tab opens.
- [ ] Video is planning-only.
- [ ] Generate MP4 button is disabled.

## Files

- [ ] Files tab opens.
- [ ] Drive folder summary is visible.
- [ ] Text/JSON preview works when files exist.

## Health / Logs

- [ ] Health / Logs tab opens.
- [ ] Ollama persistence/status is visible.
- [ ] Required folder check is visible.
- [ ] Log viewer opens when logs exist.

## Runbook

- [ ] Runbook opens.
- [ ] Operator rules are visible.
- [ ] Colab launcher command is visible.
- [ ] Checklist is visible.

## Guardrails

- [ ] Real Facebook posting disabled unless explicitly enabled and approved.
- [ ] Video generation deferred.
- [ ] No `Complete Package` tab.
- [ ] Legacy `text_workstation/app_phase110.py` not part of official validation.
