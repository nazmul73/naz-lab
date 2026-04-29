# Video Workstation Deferred Plan

Date: 2026-04-29

Status: deferred/locked until the other Naz Lab tools are stable.

## Product decision

```text
Video tab stays visible in Naz Lab.
Real video generation is not active now.
Image-to-video and MP4 rendering are deferred.
```

## Why deferred

```text
Text, Voice, Image, Review, and Facebook Post workflows should be stable first.
Video generation is heavier, more expensive, and more failure-prone.
The current v1 goal is a reliable content creation and review hub.
```

## Current allowed Video tab scope

```text
[ ] Planning-only section
[ ] Scene manifest placeholder
[ ] Future workflow explanation
[ ] Disabled Generate Video button
[ ] Clear deferred warning
```

## Future video workflow

```text
Text script
-> Scene plan
-> Image prompts
-> Generated images
-> Voice/narration
-> Video manifest
-> Image-to-video backend
-> MP4 assembly/export
```

## Future implementation phases

### Phase V1 — Scene manifest only

```text
[ ] Convert script to scene list
[ ] Create per-scene prompt
[ ] Add duration estimates
[ ] Add voice/narration link field
[ ] Save video job JSON
```

### Phase V2 — Asset bundling

```text
[ ] Bind images + voice + captions
[ ] Export video asset folder
[ ] Create render manifest
```

### Phase V3 — Real generation later

```text
[ ] Select image-to-video backend
[ ] Test GPU requirements
[ ] Add manual-gated generation controls
[ ] Generate short test clip
[ ] Add MP4 export
```

## Safety constraints

```text
No unauthorized face cloning.
No unauthorized voice cloning.
No heavy video runtime until explicitly approved.
```

## Current status

```text
Video tab: present
Real video generation: deferred
Image-to-video: deferred
MP4 rendering: deferred
```
