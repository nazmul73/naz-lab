# Social Agent / Facebook Graph API Plan

Status: PLANNED + SAFE BACKEND SKELETON READY

## Scope

The Social Agent is a semi-automated executor that reads manually approved jobs and prepares or posts content through Facebook Graph API only after explicit approval.

## Safety rules

```text
1. No automatic posting by default.
2. Manual approval is required.
3. Facebook backend config defaults to enabled=false and dry_run=true.
4. Page access token must come from environment variable, never hardcoded.
5. Approved jobs must come from social_review/approved_jobs.json.
6. Every blocked, dry-run, failed, or posted attempt is logged.
```

## Backend file

```text
social_agent/facebook_graph_backend.py
```

## Config file generated in Drive

```text
/content/drive/MyDrive/NazLab/config/facebook_graph_config.json
```

Default config:

```json
{
  "enabled": false,
  "manual_approval_required": true,
  "dry_run": true,
  "page_id": "",
  "access_token_env": "FACEBOOK_PAGE_ACCESS_TOKEN",
  "graph_api_version": "v19.0"
}
```

## Current status

Implementation-ready skeleton is complete. Real posting is intentionally blocked until the user explicitly enables config, supplies page_id/token, approves a job, and confirms manual posting.
