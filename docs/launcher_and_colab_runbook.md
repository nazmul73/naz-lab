# Launcher and Colab Runbook

Date: 2026-04-28

Status: COMPLETE

## Official launcher

```text
launchers/naz_lab_all_in_one_colab.py
```

Default target:

```text
master_dashboard/app_official.py
```

Current official app:

```text
master_dashboard/app_main.py
```

## Specialized launchers

```text
launchers/phase1_10_text_workstation_colab.py
launchers/phase3_1_real_image_backend_colab.py
```

## App map

```text
Text Workstation:
text_workstation/app_official.py

Main Hub:
master_dashboard/app_main.py

Final Package Flow:
master_dashboard/app_phase222.py

Real Image Backend:
master_dashboard/app_phase221.py

Unified Dashboard fallback:
master_dashboard/app_phase220.py

Social/Facebook Gate fallback:
master_dashboard/app_phase219.py
```

## Notebook interconnect order

```text
1. Run all-in-one launcher for Main Hub
2. Run Text Workstation launcher to create text/image job
3. Run Real Image Backend launcher with GPU to generate image
4. Run Final Package Flow dashboard to package/approve/export
5. Run Social Review/Facebook Gate only for dry-run/manual-gated social candidate
```

## Troubleshooting

### Streamlit 500

```text
1. Stop old Streamlit
2. Re-run launcher
3. Check /content/naz_lab_streamlit_<port>.log
```

### CUDA not found

```text
1. Runtime > Change runtime type > GPU
2. Restart session
3. Run real image backend launcher again
```

### No image jobs

```text
1. Open Text Workstation
2. Generate output
3. Click Send to Image Workstation
4. Confirm job exists in /content/drive/MyDrive/NazLab/job_queue/image_jobs/
```

### No packages

```text
1. Open Final Package Flow
2. Build Auto Package or Manual Prompt Package
3. Check /content/drive/MyDrive/NazLab/final_packages/
```

## Completion

Priority 6 — launcher/runbook docs complete.
