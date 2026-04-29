# Code Quality Cleanup PASS

Date: 2026-04-29

## Completed

- Added Drive-backed incremental chat autosave helper.
  - File: `shared/chat_autosave.py`
  - Saves General Chat turns as JSONL under `NazLab/chat_outputs/sessions`.
- Wired chat autosave into the Text Builder panel.
  - File: `master_dashboard/naz_lab_text_panel.py`
  - Casual chat / General Chat outputs now show the autosave session and file path.
  - Library now includes `Chat sessions` for JSONL previews.
- Updated per-workstation lightweight requirements.
  - `text_workstation/requirements.txt`
  - `voice_workstation/requirements.txt`
  - `image_workstation/requirements.txt`
  - `video_workstation/requirements.txt`
- Added conventional commit message policy.
  - File: `docs/conventional_commits.md`

## Requirement strategy

Root and workstation requirements remain lightweight for Colab dashboard startup. Heavy voice/image/video backend dependencies are intentionally deferred until those real backends are enabled.

## Commit policy

All new commits should use prefixes such as:

```text
feat:
fix:
docs:
chore:
refactor:
test:
```

## Colab verification

After launching the official dashboard:

1. Open Text > Create.
2. Run casual chat input: `how are you?`.
3. Confirm English casual reply.
4. Confirm `Chat autosave file:` appears.
5. Open Text > Library > Chat sessions.
6. Preview the latest `.jsonl` file.
