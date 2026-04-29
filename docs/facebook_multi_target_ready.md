# Facebook Multi-Target Ready

Date: 2026-04-29

Status: repo-side ready. Runtime confirmation pending in the next combined Naz Lab test.

## Requirement

```text
Facebook Post must support connecting multiple Facebook pages/profiles/accounts.
```

## Implemented

```text
Multi-target Facebook config backend
Targets list in Drive config
Default target selection
Target fields: target_key, label, target_type, target_id, access_token_env, enabled, notes
Approved package bridge to selected target
Manual Gate target override
Target-aware social post log entries
```

## Updated files

```text
social_agent/facebook_graph_backend.py
master_dashboard/naz_lab_facebook_panel.py
```

## Dashboard location

```text
Naz Lab > Facebook Post > Targets / Safe Config
Naz Lab > Facebook Post > Approved Package
Naz Lab > Facebook Post > Manual Gate
```

## Safety notes

```text
Global Facebook backend remains disabled by default.
Each target is disabled by default until explicitly enabled.
Dry-run remains true by default.
Profile targets are kept as manual handoff targets unless Graph API support is explicitly added later.
Real posting requires global enabled=true, target enabled=true, dry_run=false, page/profile target ID, token env, and manual confirmation.
```

## Test checklist

```text
Targets / Safe Config visible
Current targets table visible
Targets JSON editable
Save multi-target config works
Target page/profile selector visible in Approved Package
Bridge selected package to selected target works
Manual Gate shows target fields
Manual Gate target override visible
Safe gated attempt returns blocked/dry-run result as expected
```
