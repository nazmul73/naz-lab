# Naz Lab Reference Asset Policy

This document defines the safe workflow for any reference voice, face, portrait, or identity-related asset used inside Naz Lab.

## Core rule

Reference assets must be user-provided or explicitly authorized for the workflow.

Do not use reference voice or face assets for misleading, deceptive, unauthorized, or impersonation-style output.

## Applies to

- Voice Workstation
- Portrait Workstation
- Project Workflow Workstation packages
- Future TTS, voice clone, image, portrait, or video backend integrations

## Allowed reference asset use

Allowed when the user provides or explicitly authorizes the reference asset:

- user voice reference for the user's own narration workflow
- authorized brand/persona voice reference
- user's own portrait/photo reference
- authorized portrait reference for content planning
- style or delivery reference that does not mislead viewers

## Not allowed

Do not support:

- unauthorized celebrity voice/face cloning
- deceptive impersonation
- pretending a generated voice/video is a real person when it is not
- using a reference asset without permission
- hiding that a voice/portrait is generated when disclosure is needed
- using reference assets to mislead, scam, defame, or manipulate viewers

## Voice reference rules

Voice reference workflows should require:

- uploaded reference audio path
- confirmation that the asset is user-provided or explicitly authorized
- notes describing intended use
- package metadata recording the reference policy

Recommended allowed audio file types:

```text
.mp3
.wav
.m4a
.ogg
.flac
```

Recommended Drive folder:

```text
/content/drive/MyDrive/NazLab/voice_references
```

Recommended package fields:

```json
{
  "reference_voice_path": "",
  "reference_voice_authorized": false,
  "reference_voice_notes": "",
  "reference_policy": "Reference voice requires user-provided or explicitly authorized audio."
}
```

## Portrait / face reference rules

Portrait reference workflows should require:

- uploaded reference image path
- confirmation that the asset is user-provided or explicitly authorized
- notes describing intended use
- no misleading identity claim

Recommended allowed image file types:

```text
.jpg
.jpeg
.png
.webp
```

Recommended Drive folder:

```text
/content/drive/MyDrive/NazLab/portrait_references
```

Recommended package fields:

```json
{
  "reference_image_path": "",
  "reference_image_authorized": false,
  "reference_image_notes": "",
  "reference_policy": "Reference image requires user-provided or explicitly authorized image."
}
```

## Metadata requirements

Any package that uses a reference asset should include:

- asset path
- authorization boolean
- user notes
- created timestamp
- workstation name
- intended use
- reference policy text

## UI requirements

Reference managers should show:

- reference folder path
- upload area
- saved reference list
- selected reference path
- authorization checkbox
- notes field
- package preview
- warning against unauthorized use

## Safer default

If authorization is not confirmed, the app should still allow generic/original output planning, but should not mark the package as reference-authorized.

## Future backend rule

When real generation backends are added, any backend that uses a reference asset should check the authorization metadata before allowing reference-based generation.
