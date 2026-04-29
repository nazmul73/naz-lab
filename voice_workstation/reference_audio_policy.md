# Reference Audio Policy

Naz Lab voice workflows may only use reference audio that is user-provided or explicitly authorized.

## Allowed

- Audio recorded by the user.
- Audio uploaded by the user with permission to use it as a reference.
- Public or licensed audio only when the license explicitly allows the intended reference workflow.
- Internal test audio created for Naz Lab testing.

## Not allowed

- Audio copied from a private person without consent.
- Celebrity, creator, or public-figure voice references without explicit authorization.
- Hidden recordings or surveillance-style audio.
- Audio intended to impersonate, deceive, or mislead.

## UI requirement

Any future reference-audio workflow should show an explicit consent checkbox:

```text
I confirm this reference audio is user-provided or explicitly authorized for this Naz Lab workflow.
```

The workflow should not create a reference voice job unless this confirmation is checked.

## Storage path

Reference audio should be stored under:

```text
/content/drive/MyDrive/NazLab/voice_outputs/reference_audio
```

## Current status

Voice generation is currently job/planning-oriented. Real TTS or voice cloning backends should remain disconnected until consent, logging, and audit metadata are fully implemented.
