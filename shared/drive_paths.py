"""Shared Google Drive path constants for the Naz Lab ecosystem.

This module intentionally contains no heavy dependencies. It is safe to import
from Colab setup scripts and future workstation apps.
"""

from __future__ import annotations

from pathlib import Path

BASE_PATH = Path("/content/drive/MyDrive/NazLab")

TEXT_OUTPUTS = BASE_PATH / "text_outputs"
CHAT_OUTPUTS = BASE_PATH / "chat_outputs"
SCRIPT_OUTPUTS = BASE_PATH / "script_outputs"
IMAGE_PROMPTS = BASE_PATH / "image_prompts"

IMAGE_OUTPUTS = BASE_PATH / "image_outputs"
VOICE_OUTPUTS = BASE_PATH / "voice_outputs"
VIDEO_OUTPUTS = BASE_PATH / "video_outputs"
FACEFUSION_OUTPUTS = BASE_PATH / "facefusion_outputs"
LIVEPORTRAIT_OUTPUTS = BASE_PATH / "liveportrait_outputs"

JOB_QUEUE = BASE_PATH / "job_queue"
IMAGE_JOBS = JOB_QUEUE / "image_jobs"
VOICE_JOBS = JOB_QUEUE / "voice_jobs"
VIDEO_JOBS = JOB_QUEUE / "video_jobs"
FACE_JOBS = JOB_QUEUE / "face_jobs"
COMPLETED_JOBS = JOB_QUEUE / "completed_jobs"

MODELS_DIR = BASE_PATH / "models"
OLLAMA_MODELS = MODELS_DIR / "ollama"
TEMP_DIR = BASE_PATH / "temp"

METADATA_DIR = BASE_PATH / "metadata"
TEXT_METADATA = METADATA_DIR / "text"

CONFIG_DIR = BASE_PATH / "config"
LOGS_DIR = BASE_PATH / "logs"

WORKSTATION_LINKS_JSON = CONFIG_DIR / "workstation_links.json"
CUSTOM_GEMS_JSON = CONFIG_DIR / "custom_gems.json"
TOOL_LINKS_JSON = CONFIG_DIR / "tool_links.json"
OUTPUT_LOG_JSON = LOGS_DIR / "output_log.json"

REQUIRED_DIRECTORIES = [
    TEXT_OUTPUTS,
    CHAT_OUTPUTS,
    SCRIPT_OUTPUTS,
    IMAGE_PROMPTS,
    IMAGE_OUTPUTS,
    VOICE_OUTPUTS,
    VIDEO_OUTPUTS,
    FACEFUSION_OUTPUTS,
    LIVEPORTRAIT_OUTPUTS,
    JOB_QUEUE,
    IMAGE_JOBS,
    VOICE_JOBS,
    VIDEO_JOBS,
    FACE_JOBS,
    COMPLETED_JOBS,
    MODELS_DIR,
    OLLAMA_MODELS,
    TEMP_DIR,
    METADATA_DIR,
    TEXT_METADATA,
    CONFIG_DIR,
    LOGS_DIR,
]

REQUIRED_JSON_FILES = [
    WORKSTATION_LINKS_JSON,
    CUSTOM_GEMS_JSON,
    TOOL_LINKS_JSON,
    OUTPUT_LOG_JSON,
]
