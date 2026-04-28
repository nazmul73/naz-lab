# Official App Structure Policy

Date: 2026-04-28

Status: COMPLETE

## Official entrypoints

```text
Text Workstation:
text_workstation/app_official.py

Master Dashboard:
master_dashboard/app_official.py

All-in-one launcher:
launchers/naz_lab_all_in_one_colab.py
```

## Current implementation apps

```text
Text Workstation stable implementation:
text_workstation/app_phase110.py

Final Content Package Flow dashboard:
master_dashboard/app_phase222.py

Real Image Backend dashboard:
master_dashboard/app_phase221.py

Unified frontend dashboard:
master_dashboard/app_phase220.py
```

## Legacy fallback policy

```text
text_workstation/app.py
- Keep as legacy fallback for older launchers.
- Do not delete until official wrapper and all-in-one launcher pass runtime tests.

master_dashboard/app.py
- Keep as legacy fallback for package search and older dashboard runs.
- Do not delete until official wrapper and all-in-one launcher pass runtime tests.
```

## Phase app policy

```text
app_phase217.py — queue/text/image visibility fallback
app_phase218.py — image bridge/social review fallback
app_phase219.py — model health/Facebook gate fallback
app_phase220.py — unified frontend fallback
app_phase221.py — real image backend app
app_phase222.py — final package flow app
```

## Cleanup rule

Runtime test is not required for this policy document. Runtime tests are required before deleting or replacing legacy `app.py` files.
