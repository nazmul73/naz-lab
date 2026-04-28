# Safety and Deferred Scopes

Date: 2026-04-28

Status: COMPLETE

## Locked / disabled by design

```text
Real Facebook posting — disabled by default
Automatic social posting — not allowed without manual approval
Unauthorized voice cloning — not supported
Unauthorized face cloning — not supported
Real video generation — deferred after v1
Image-to-video generation — deferred after v1
```

## Facebook gate

Default config path:

```text
/content/drive/MyDrive/NazLab/config/facebook_graph_config.json
```

Required safe defaults:

```json
{
  "enabled": false,
  "manual_approval_required": true,
  "dry_run": true
}
```

Real posting requires:

```text
1. User explicitly enables config
2. page_id exists
3. token is provided through environment variable only
4. approved job/package exists
5. manual confirmation gate is checked
```

## Reference image policy

Reference image package mode stores paths/copies for packaging and future reference-aware image generation. Use only images the user has rights to use.

## Video scope

Naz Lab v1 supports content planning, image generation, packages, approval, and export. It does not render video/MP4 by default.

## Completion

Priority 5 — safety/locked scope docs complete.
