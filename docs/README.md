# Naz Lab Docs Index

This folder contains project-level guidance for Naz Lab.

## Core docs

- `bangla_quality_engine.md` — Global Bangla-first quality rules.
- `voice_video_bangla_quality.md` — Bangla quality rules for Voice and Video workflows.
- `reference_asset_policy.md` — Safe reference voice/face/portrait asset policy.
- `backend_planning.md` — Backend planning foundation for future heavy generation tools and adapters.
- `final_integration_checklist.md` — Final integration readiness checklist before backend adapter skeletons.
- `backend_adapter_skeleton_runbook.md` — Lightweight backend skeleton command runbook.
- `generic_tts_backend_runbook.md` — First real backend target runbook for safe generic TTS.
- `image_prompt_backend_runbook.md` — Image prompt-to-output placeholder backend runbook.
- `video_placeholder_backend_runbook.md` — Video placeholder backend runbook.
- `final_reel_pack_assembly_runbook.md` — Final reel pack JSON/Markdown assembly runbook.
- `final_verification_runbook.md` — Final lightweight verification runbook for smoke test, final pack, and Dashboard Phase 2.14.
- `naz_lab_v1_finalization_plan.md` — Naz Lab v1 finalization scope with real video generation deferred.
- `naz_lab_v1_ready.md` — Naz Lab v1 ready marker after final verification.
- `naz_lab_v1_practical_use_marker.md` — v1 practical-use readiness marker.
- `input_test_console_pass.md` — Input Test Console and Dashboard integration pass marker.
- `dashboard_2_15_input_console_pass.md` — Dashboard Phase 2.15 Input Test Console integration pass marker.
- `real_content_package_trial_protocol.md` — Practical real content package trial protocol.
- `real_trials_finalization_checklist.md` — Real package trial finalization checklist.
- `toolflow_real_trial_protocol.md` — ToolFlow real package trial protocol, ready for user test.
- `toolflow_dashboard_verification_runbook.md` — ToolFlow Dashboard Package Search verification runbook.
- `real_trials_completion_prep.md` — Real Content Package Trials completion prep, without PASS marker.
- `v1_5_backend_target_options.md` — v1.5 backend target decision prep.
- `general_bangla_real_trial_pass.md` — General Bangla real content package trial pass marker.
- `true_noir_real_trial_pass.md` — True Noir Tales real content package trial pass marker.
- `backend_next_phase_freeze.md` — Backend next-phase freeze for v1 practical completion.
- `video_generation_deferred_lock.md` — Locked deferred status for real video generation.
- `video_generation_deferred_roadmap.md` — Future v1.5/v2 roadmap for real video generation.
- `dashboard_v1_readiness_note.md` — Dashboard Phase 2.14 interpretation for Naz Lab v1 final verification.
- `../backend_adapters/README.md` — Backend Adapter Skeletons 1.0 overview and run commands.
- `../launchers/all_in_one_colab_launcher.md` — Robust one-click Colab launcher with Cloudflare public URL handling.
- `../launchers/input_test_console_one_cell.md` — One-cell frontend launcher for Input Test Console.
- `../launchers/input_test_console_colab_proxy.md` — Colab proxy launcher for Input Test Console when Cloudflare is unreliable.

## Current marker

```text
Naz Lab v1 — Ready
Video generation — Locked / Deferred after v1
Frontend Input Test Console — PASS
Dashboard Phase 2.16.1 — HOTFIX READY FOR USER TEST
Dashboard Final Packs integration — PASS
Dashboard Package Search integration — HOTFIX READY
Dashboard Deep JSON Search — HOTFIX READY
Real Content Package Trial — ACTIVE
General Bangla Real Trial — PASS
True Noir Tales Real Trial — PASS
ToolFlow Real Trial — SAVED, DASHBOARD VERIFICATION PENDING
Backend Next Phase — FROZEN UNTIL REAL TRIALS COMPLETE
```

## v1 practical-use rule

Naz Lab v1 supports practical content planning and packaging, not real video generation.

Included now:

- topic input
- text/script package
- image prompt package
- generic voice/TTS plan package
- video planning manifest
- posting package
- package save to Drive
- Dashboard preview/search/export
- backend placeholder adapters and queue scanning

Not included now:

- real AI video generation
- rendered MP4 assembly
- image-to-video generation
- heavy GPU generation runtime
- unauthorized voice/face cloning

## Key language rules

Naz Lab is Bangla-first by default.

Bangla should be:

- natural spoken Bangla
- Facebook-ready
- netizen-friendly
- voiceover-ready
- subtitle-friendly when used in video
- simple and human
- not stiff textbook Bangla

Default regional flavor:

- Rangpur / Nilphamari / North Bengal

Secondary tones supported when requested:

- Dhakaiya
- Chattogram
- Sylhet
- Noakhali / Comilla

## Safety reminders

- Use adult-only subjects for true-crime/noir content.
- Avoid gore, dead bodies, visible wounds, and exposed violence.
- Use Bangladeshi people and scenarios by default for general Naz Lab visuals.
- Women should have no sindoor unless explicitly requested.
- Reference face/voice workflows require user-provided or explicitly authorized reference assets.
- Generic TTS backend must not perform voice cloning.
- Image placeholder backend must not claim to create final AI artwork.
- Video placeholder backend must not claim to create final rendered video.
- Final reel pack assembler must not claim to render final MP4.
- Dashboard v1 readiness does not include real video generation.
- Real video generation is locked/deferred until after v1 practical trials complete and the user explicitly chooses a new backend target.

## Backend planning rules

Backend generation should stay separate from the Master Dashboard.

Heavy tools such as Fooocus, Stable Diffusion, XTTS, video generation tools, LivePortrait, and FaceFusion should run in isolated workstation runtimes or future backend adapters.

Backend next phase is frozen until:

1. ToolFlow real content package trial passes.
2. Real Content Package Trials complete marker exists.
3. The user explicitly chooses the next backend target.
4. Runtime/dependency planning is done separately.

## Current build status

- Voice Workstation safer reference manager integration — done and tested.
- Portrait Workstation safer reference manager integration — done and tested.
- Dashboard Package Search download/export buttons — done and tested.
- Dashboard Package Search deep JSON search — hotfix prepared in Phase 2.16.1.
- Dashboard Phase 2.16.1 — hotfix committed, pending user Dashboard verification.
- ToolFlow Dashboard verification runbook — prepared.
- Real trials completion prep — prepared, not marked complete.
- v1.5 backend target options — prepared for later decision.
- Backend planning foundation — done.
- Final integration checklist — done.
- Backend Adapter Skeletons 1.0 — done as lightweight skeleton, no heavy generation tools installed.
- Dashboard backend status panel — done.
- Backend skeleton command runbook — done.
- Generic TTS Backend Runbook 1.0 — done.
- Generic gTTS backend adapter — done and tested by user.
- Image Prompt Backend Runbook 1.0 — done.
- Image placeholder backend adapter — done and tested by user.
- Video Placeholder Backend Runbook 1.0 — done.
- Video placeholder backend adapter — done and tested by user.
- Final Reel Pack Assembly Runbook 1.0 — done.
- Final reel pack assembler — done and tested by user.
- Dashboard final reel pack tab — done and final-verified.
- Dashboard Phase 2.15 Input Console integration — done and verified.
- Frontend Input Test Console — done and passed.
- Real Content Package Trial Protocol — active.
- General Bangla real content package trial — passed.
- True Noir Tales real content package trial — passed.
- ToolFlow real content package trial — saved, Dashboard verification pending.
- Real trials finalization checklist — active.
- Naz Lab v1 practical use marker — ready, pending ToolFlow final test.
- Backend next phase freeze — active.
- Video generation deferred lock — active.
- One-cell Input Test Console launcher — done.
- Colab proxy Input Test Console launcher — done.
- Robust all-in-one Colab launcher — done.
- Lightweight integration smoke test — done.
- Final verification runbook — done.
- Naz Lab v1 finalization plan — done.
- Naz Lab v1 ready marker — done.
- Video generation deferred roadmap — done.

## Recommended next work

1. Run Dashboard Phase 2.16.1 hotfix in Colab.
2. Verify ToolFlow package in Dashboard Package Search.
3. Add ToolFlow pass marker after user verification.
4. Add Real Content Package Trials complete marker after ToolFlow pass.
5. Then choose one next backend target for v1.5.
