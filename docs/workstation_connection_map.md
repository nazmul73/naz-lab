# Workstation Connection Map

Date: 2026-04-28

Status: COMPLETE

## Core storage root

```text
/content/drive/MyDrive/NazLab/
```

## Main data connectors

```text
Text outputs:
/content/drive/MyDrive/NazLab/text_outputs/

Script outputs:
/content/drive/MyDrive/NazLab/script_outputs/

Image prompts:
/content/drive/MyDrive/NazLab/image_prompts/

Image jobs:
/content/drive/MyDrive/NazLab/job_queue/image_jobs/

Image outputs:
/content/drive/MyDrive/NazLab/image_outputs/

Social review:
/content/drive/MyDrive/NazLab/social_review/

Final packages:
/content/drive/MyDrive/NazLab/final_packages/

Reference images:
/content/drive/MyDrive/NazLab/reference_images/

Logs:
/content/drive/MyDrive/NazLab/logs/
```

## Workstation flow

```text
Text Workstation
-> saves text/script/prompt outputs
-> creates image_job JSON
-> sends to Image Workstation through job_queue/image_jobs

Image Workstation
-> reads image_job JSON
-> generates placeholder manifest or real PNG
-> writes image_outputs
-> updates image_job output_path and output_metadata_path

Final Package Flow
-> reads text output + image job + generated image + metadata
-> builds final package JSON
-> supports auto, manual prompt, and reference image package modes
-> exports package folder
-> writes approved package list

Social Review
-> reads image jobs / approved jobs
-> approves/rejects candidates
-> writes approved_jobs.json and rejected_jobs.json

Facebook Gate
-> reads approved jobs/packages
-> defaults to disabled + dry_run
-> requires manual approval before any real post attempt
```

## Text -> Image connection

```text
Source app:
text_workstation/app_phase110.py

Official entrypoint:
text_workstation/app_official.py

Output:
/content/drive/MyDrive/NazLab/job_queue/image_jobs/image_job_*.json

Schema:
schema_version = 1.10
source_workstation = text_workstation
target_workstation = image_workstation
status = queued
review_status = pending
```

## Image -> Final Package connection

```text
Source backend:
image_workstation/real_image_backend_phase31.py

Dashboard:
master_dashboard/app_phase221.py

Output:
/content/drive/MyDrive/NazLab/image_outputs/*.png
/content/drive/MyDrive/NazLab/image_outputs/*.metadata.json

Job update:
output_path = generated PNG path
output_metadata_path = metadata JSON path
status = done
```

## Final Package -> Social Review connection

```text
Source backend:
final_package/package_backend.py

Dashboard:
master_dashboard/app_phase222.py

Output:
/content/drive/MyDrive/NazLab/final_packages/*.json
/content/drive/MyDrive/NazLab/final_packages/approved/*.json
/content/drive/MyDrive/NazLab/final_packages/approved_packages.json

Next consumer:
Social Review / Facebook Gate
```

## Social Review -> Facebook Gate connection

```text
Social Review approved jobs:
/content/drive/MyDrive/NazLab/social_review/approved_jobs.json

Final approved packages:
/content/drive/MyDrive/NazLab/final_packages/approved_packages.json

Facebook config:
/content/drive/MyDrive/NazLab/config/facebook_graph_config.json

Default:
enabled = false
dry_run = true
manual_approval_required = true
```

## Future workstations

```text
Voice Workstation — planned/future backend
Video Workstation — deferred after v1
Portrait Workstation — planned/future backend
Face/LivePortrait — planned/future backend if needed
```

Each future workstation must connect through:

```text
/content/drive/MyDrive/NazLab/job_queue/<station>_jobs/
/content/drive/MyDrive/NazLab/<station>_outputs/
shared schema validation
Dashboard status/preview tab
```

## Completion

Priority 3 — Workstation connection docs are complete at the repo/docs level. Runtime tests remain separate.
