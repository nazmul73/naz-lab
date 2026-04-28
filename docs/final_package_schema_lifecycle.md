# Final Package Schema and Lifecycle

Date: 2026-04-28

Status: COMPLETE

## Backend

```text
final_package/package_backend.py
```

## Dashboard

```text
master_dashboard/app_phase222.py
```

## Storage

```text
/content/drive/MyDrive/NazLab/final_packages/
/content/drive/MyDrive/NazLab/final_packages/approved/
/content/drive/MyDrive/NazLab/final_packages/exports/
/content/drive/MyDrive/NazLab/reference_images/
```

## Package schema

```json
{
  "package_id": "pkg_xxx",
  "schema_version": "1.0",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime",
  "project": "General Bangla",
  "topic": "topic or brief",
  "status": "draft | ready | approved | rejected | exported",
  "review_status": "pending | approved | rejected",
  "source_mode": "auto_job | manual_prompt | manual_prompt_with_reference",
  "text_output_path": "Drive path to text output",
  "image_job_path": "Drive path to image job JSON",
  "generated_image_path": "Drive path to generated PNG/JPG/WebP",
  "image_metadata_path": "Drive path to metadata JSON",
  "manual_prompt": "custom image prompt or source prompt",
  "reference_images": [],
  "caption_text": "caption or post copy",
  "notes": "operator notes",
  "package_assets": {},
  "history": []
}
```

## Lifecycle

```text
draft
-> ready
-> approved
-> exported
```

Alternative branch:

```text
draft/ready -> rejected
```

## Status meanings

```text
draft — package exists but may not yet have all assets
ready — package has enough assets to review/export
approved — package passed manual review
rejected — package should not be used
exported — package assets copied to an export folder
```

## Source modes

### Auto package

```text
source_mode = auto_job
```

Uses:

```text
text_output_path
image_job_path
generated_image_path from job output_path
image_metadata_path from job output_metadata_path
```

### Manual prompt package

```text
source_mode = manual_prompt
```

Uses:

```text
manual_prompt
optional generated_image_path
optional caption_text
```

### Manual prompt + reference image package

```text
source_mode = manual_prompt_with_reference
```

Uses:

```text
manual_prompt
reference_images
optional generated_image_path
optional caption_text
```

Reference images are copied into:

```text
/content/drive/MyDrive/NazLab/reference_images/
```

## Export behavior

Export copies available assets into:

```text
/content/drive/MyDrive/NazLab/final_packages/exports/<package_id>/
```

Typical exported files:

```text
package.json
text output file
image job JSON
generated image
image metadata JSON
reference images
```

## Approved package list

Approved package index:

```text
/content/drive/MyDrive/NazLab/final_packages/approved_packages.json
```

Approved package copies:

```text
/content/drive/MyDrive/NazLab/final_packages/approved/*.json
```

## Runtime-independent completion

Priority 4 — Final package backend/schema/lifecycle docs are complete. Runtime tests remain separate.
