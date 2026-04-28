# ToolFlow Dashboard Verification Runbook

Status: verification-ready, not passed yet  
Dashboard target: Phase 2.16.1 package-search hotfix  
PASS authority: user confirmation only

## Purpose

This runbook verifies that the ToolFlow package saved from Input Test Console can be found through the Master Dashboard Package Search, including deep JSON/content search.

## Required Dashboard behavior

The Dashboard Package Search must find saved packages by:

- filename
- folder/path
- project field
- workflow field
- topic/audience/direction fields
- full nested JSON content
- normalized token matching for identifiers such as `frontend_full_package_toolflow`

## Required search keywords

Search these keywords one by one in Dashboard -> Package Search:

```text
ToolFlow
under 30 minutes
small business owners
frontend_full_package_toolflow
```

Recommended filters:

```text
Folder: All package folders
Project contains: blank
Status contains: blank
Latest files per folder: 500 or higher
Match mode: Token match
```

## PASS criteria

ToolFlow Dashboard verification can only pass if all are true:

```text
ToolFlow: found
under 30 minutes: found
small business owners: found
frontend_full_package_toolflow: found
Preview: working
Download JSON/Markdown/TXT or report export: working
No Dashboard error shown
```

## Not allowed

Do not create or commit ToolFlow PASS marker until the user explicitly says:

```text
Dashboard verification done
```

## If verification fails

If one or more keywords are not found:

1. Do not mark PASS.
2. Inspect the latest saved package content.
3. Confirm whether the package was saved as Full Content Package from Input Test Console.
4. Confirm whether the missing phrases exist in the saved JSON.
5. Fix search/indexing/package metadata if needed.

## Current preparation status

- Dashboard Phase 2.16.1 hotfix adds recursive JSON scan.
- Package Search supports token matching and exact phrase matching.
- ToolFlow verification helper displays keyword discovery status.
- This runbook is prepared before final user verification.
