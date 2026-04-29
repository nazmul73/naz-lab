"""Official Text Workstation helper functions.

This module replaces legacy helper imports from text_workstation/app_phase110.py.
It intentionally contains no standalone Streamlit UI, no weak model list, no old
ChatML generation path, and no duplicate image job creation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from shared.drive_paths import (
    BASE_PATH,
    CHAT_OUTPUTS,
    IMAGE_JOBS,
    IMAGE_PROMPTS,
    OUTPUT_LOG_JSON,
    SCRIPT_OUTPUTS,
    TEXT_OUTPUTS,
    WORKSTATION_LINKS_JSON,
)
from shared.json_utils import append_output_log, safe_write_json, update_workstation_status
from shared.model_policy import ALLOWED_TEXT_MODELS, MINIMUM_CPU_TEXT_MODEL, RECOMMENDED_TEXT_MODEL
from shared.ollama_text_generation import user_requested_bangla

PHASE = "1.20-helper"
PHASE_STATUS = "official-shared-text-helper"
OLLAMA_HEALTH_ENDPOINT = "http://localhost:11434/api/tags"
DEFAULT_NEGATIVE_PROMPT = "no fake logo, no watermark, no distorted face"
BANGLA_RE = re.compile(r"[\u0980-\u09FF]")
BROKEN_MARKERS = ["জাতিরূপে", "ইকাশন", "ইনস্ট স্ট্যার", "অভিমান করে ফেলল", "এই জাতিরূপে", "অভিযান করল"]

MODE_CONFIG = {
    "General Chat": {"output_dir": CHAT_OUTPUTS, "prefix": "general_chat", "auto_save": False, "template_default": False},
    "Free Writer": {"output_dir": TEXT_OUTPUTS, "prefix": "free_writer", "auto_save": False, "template_default": False},
    "Story Writer": {"output_dir": TEXT_OUTPUTS, "prefix": "story_writer", "auto_save": True, "template_default": True},
    "Viral Script Writer": {"output_dir": SCRIPT_OUTPUTS, "prefix": "viral_script_writer", "auto_save": True, "template_default": True},
    "Caption Writer": {"output_dir": TEXT_OUTPUTS, "prefix": "caption_writer", "auto_save": False, "template_default": True},
    "Prompt Improver": {"output_dir": IMAGE_PROMPTS, "prefix": "prompt_improver", "auto_save": False, "template_default": True},
    "YouTube Script": {"output_dir": SCRIPT_OUTPUTS, "prefix": "youtube_script", "auto_save": False, "template_default": True},
}


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")[:80] or "naz_lab"


def ensure_dirs() -> None:
    for folder in [BASE_PATH, CHAT_OUTPUTS, TEXT_OUTPUTS, SCRIPT_OUTPUTS, IMAGE_PROMPTS, IMAGE_JOBS, WORKSTATION_LINKS_JSON.parent, OUTPUT_LOG_JSON.parent]:
        folder.mkdir(parents=True, exist_ok=True)
    if not WORKSTATION_LINKS_JSON.exists():
        safe_write_json(WORKSTATION_LINKS_JSON, {})
    if not OUTPUT_LOG_JSON.exists():
        safe_write_json(OUTPUT_LOG_JSON, {"logs": []})


def bangla_quality_score(text: str) -> int:
    stripped = text.strip()
    score = 100
    if len(stripped) < 60:
        score -= 25
    if len(BANGLA_RE.findall(stripped)) < 25:
        score -= 30
    for marker in BROKEN_MARKERS:
        if marker in stripped:
            score -= 30
    return max(score, 0)


def needs_safe_bangla(user_input: str, language: str, output: str, bangla_safe_mode: bool) -> bool:
    if not bangla_safe_mode:
        return False
    if not user_requested_bangla(user_input, language):
        return False
    return bangla_quality_score(output) < 70


def template_chat(topic: str) -> str:
    return f"""আপনি লিখেছেন: {topic}

আমি বিষয়টা বুঝেছি। আপনি চাইলে এটাকে পোস্ট, স্ক্রিপ্ট, ক্যাপশন, গল্প, image prompt অথবা content workflow-তে রূপ দিতে পারেন।

এই ইনপুট নিয়ে এখন কোন ধরনের আউটপুট চান?"""


def template_story(topic: str) -> str:
    return f"""Title
AI দিয়ে ছোট ব্যবসার নতুন শুরু

Setup
একজন ছোট ব্যবসায়ী প্রতিদিন কনটেন্ট বানাতে গিয়ে সমস্যায় পড়তেন। দোকান সামলানো, কাস্টমারের মেসেজের উত্তর দেওয়া, নতুন পোস্টের আইডিয়া বের করা—সব একসাথে সামলানো সহজ ছিল না।

Main Event
একদিন তিনি সিদ্ধান্ত নিলেন, কাজটা এলোমেলোভাবে না করে AI tools দিয়ে একটি সহজ workflow বানাবেন। বিষয় ছিল: {topic}। তিনি প্রথমে বিষয় লিখলেন, তারপর সেটাকে পোস্টের লেখা, ছবির ধারণা, ক্যাপশন আর ছোট ভিডিওর স্ক্রিপ্টে ভাগ করলেন।

Turning Point
আগে যে কাজ করতে অনেক সময় লাগত, এখন সেটা ধাপে ধাপে সহজ হয়ে গেল। তিনি বুঝলেন, AI শুধু নতুন টুল না; ঠিকভাবে ব্যবহার করলে এটা প্রতিদিনের কাজ গুছিয়ে দিতে পারে।

Ending
এরপর থেকে তিনি প্রতিদিন নতুন করে শুরু না করে একটি নিয়মিত পদ্ধতি ব্যবহার করতে লাগলেন। এতে সময় বাঁচল, কাজ পরিষ্কার হলো, আর কনটেন্ট বানানো নিয়ে ভয়ও কমে গেল।

Question CTA
আপনি হলে আপনার ব্যবসার কোন কাজটা আগে AI দিয়ে সহজ করতেন?"""


def template_script(topic: str) -> str:
    return f"""Title
AI দিয়ে ছোট ব্যবসার কনটেন্ট সহজ করার উপায়

Hook
প্রতিদিন কনটেন্ট বানাতে গিয়ে আটকে গেলে নতুন টুল নয়, আগে দরকার একটি সহজ workflow।

Voiceover
অনেক ছোট ব্যবসায়ী ভালো পণ্য বা সার্ভিস থাকা সত্ত্বেও নিয়মিত পোস্ট করতে পারেন না। কারণ আইডিয়া, লেখা, ছবি আর ক্যাপশন—সব একসাথে সামলানো কঠিন।

AI tools ব্যবহার করলে কাজটা ধাপে ধাপে করা যায়। প্রথমে বিষয় লিখুন: {topic}। এরপর সেটাকে পোস্ট, স্ক্রিপ্ট, image prompt আর caption-এ ভাগ করুন।

এভাবে AI আপনার হয়ে ব্যবসা চালাবে না, কিন্তু আপনার content planning অনেক সহজ করে দেবে।

On-screen text
AI tools + simple workflow = faster content planning

Caption
ছোট ব্যবসার কনটেন্ট বানাতে AI tools তখনই কাজে লাগে, যখন সেটাকে একটি নিয়মিত workflow-এর অংশ করা যায়।

CTA
আপনি কোন অংশটা আগে automate করতে চান?"""


def template_youtube_script(topic: str) -> str:
    return f"""Title
{topic}

Intro Hook
আজকের ভিডিওতে আমরা সহজভাবে দেখব—এই বিষয়টা কেন গুরুত্বপূর্ণ এবং কীভাবে এটাকে বাস্তবে কাজে লাগানো যায়।

Main Points
১. সমস্যাটা কী
অনেক সময় আমরা কাজ শুরু করি, কিন্তু পরিষ্কার কাঠামো না থাকলে মাঝপথে আটকে যাই।

২. সমাধানের সহজ পথ
প্রথমে বিষয়টা ছোট ধাপে ভাগ করুন। তারপর প্রতিটি ধাপের জন্য আলাদা content, visual, caption এবং action plan তৈরি করুন।

৩. ব্যবহারিক উদাহরণ
ধরুন আপনার বিষয় হলো: {topic}। এটাকে একটি hook, তিনটি main point, একটি example এবং একটি CTA-তে ভাগ করলে ভিডিও বানানো সহজ হয়।

Closing CTA
এই ধরনের workflow আপনার কাজে লাগবে মনে হলে, পরের ভিডিওতে কোন বিষয় চান?"""


def template_caption(topic: str) -> str:
    return f"""Caption 1
ছোট ব্যবসার কনটেন্ট বানানো কঠিন মনে হলে আগে কাজটা ছোট ছোট ধাপে ভাগ করুন। একটি বিষয় নিন, তারপর AI tools দিয়ে পোস্টের লেখা, ক্যাপশন, image prompt আর reel idea তৈরি করুন।

বিষয়: {topic}

আপনি হলে কোন ধাপটা আগে automate করতেন?

Caption 2
AI tools ব্যবহার করার আসল সুবিধা হলো—এটা আপনার কাজ গুছিয়ে দিতে পারে। প্রতিদিন নতুন করে ভাবার বদলে একটি fixed workflow ব্যবহার করুন।

Caption 3
ছোট ব্যবসার জন্য নিয়মিত কনটেন্ট দরকার, কিন্তু সবসময় সময় থাকে না। AI tools দিয়ে content planning করলে কাজটা দ্রুত, সহজ এবং repeatable হয়।"""


def template_prompt(topic: str) -> str:
    return f"""Clean modern productivity visual of a Bangladeshi small business owner using AI tools on a laptop, organized content planning workflow visible on screen, realistic office or shop environment, natural light, premium but practical social media aesthetic, adult subject only, clear face, clean composition, Facebook-ready image.

Topic: {topic}

Negative prompt: {DEFAULT_NEGATIVE_PROMPT}"""


def template_free(topic: str) -> str:
    return f"""{topic}

ছোট ব্যবসার জন্য নিয়মিত কনটেন্ট বানানো অনেক সময় কঠিন হয়ে যায়। প্রতিদিন নতুন আইডিয়া বের করা, পোস্ট লেখা, ক্যাপশন বানানো, ছবির ধারণা তৈরি করা—সবকিছু একসাথে করলে কাজটা ভারী লাগে।

AI tools ব্যবহার করলে এই কাজগুলো ধাপে ধাপে সহজ করা যায়। প্রথমে একটি বিষয় ঠিক করুন। তারপর সেই বিষয় থেকে পোস্টের লেখা, image prompt, caption এবং ছোট ভিডিওর idea তৈরি করুন।

এভাবে AI আপনার জায়গায় ব্যবসা চালাবে না, কিন্তু আপনার planning দ্রুত ও পরিষ্কার করে দেবে।

আপনি হলে আপনার content workflow-এর কোন অংশটা আগে automate করতেন?"""


def template_output(mode: str, topic: str) -> str:
    clean_topic = " ".join(topic.strip().split()) or "AI tools দিয়ে ছোট ব্যবসার content planning"
    if mode == "General Chat":
        return template_chat(clean_topic)
    if mode == "Story Writer":
        return template_story(clean_topic)
    if mode == "Viral Script Writer":
        return template_script(clean_topic)
    if mode == "YouTube Script":
        return template_youtube_script(clean_topic)
    if mode == "Caption Writer":
        return template_caption(clean_topic)
    if mode == "Prompt Improver":
        return template_prompt(clean_topic)
    return template_free(clean_topic)


def get_ollama_tags() -> dict[str, Any]:
    response = requests.get(OLLAMA_HEALTH_ENDPOINT, timeout=15)
    response.raise_for_status()
    return response.json()


def installed_model_names() -> list[str]:
    try:
        tags = get_ollama_tags()
        return [item.get("name", "") for item in tags.get("models", []) if item.get("name")]
    except Exception:
        return []


def model_installed(model: str) -> bool:
    return any(name == model or name.startswith(f"{model}:") for name in installed_model_names())


def save_text_output(mode: str, project: str, language: str, topic: str, content: str, engine_status: str) -> Path:
    config = MODE_CONFIG.get(mode, MODE_CONFIG["Free Writer"])
    output_dir = config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{config['prefix']}_{safe_slug(project)}_{safe_slug(topic)}_{now_stamp()}.txt"
    header = {"phase": PHASE, "project": project, "mode": mode, "language": language, "topic": topic, "engine_status": engine_status, "created_at": now_iso()}
    path.write_text("# Naz Lab Text Output\n\n```json\n" + json.dumps(header, ensure_ascii=False, indent=2) + "\n```\n\n" + content, encoding="utf-8")
    append_output_log(OUTPUT_LOG_JSON, workstation="text_workstation", event="output_saved", details={"path": str(path), "mode": mode, "engine_status": engine_status})
    update_workstation_status(WORKSTATION_LINKS_JSON, "text_workstation", {"status": PHASE_STATUS, "phase": PHASE, "last_output_path": str(path)})
    return path


def helper_status() -> dict[str, Any]:
    return {
        "phase": PHASE,
        "status": PHASE_STATUS,
        "allowed_models": ALLOWED_TEXT_MODELS,
        "recommended_model": RECOMMENDED_TEXT_MODEL,
        "minimum_model": MINIMUM_CPU_TEXT_MODEL,
        "contains_generation_backend": False,
        "contains_standalone_ui": False,
        "contains_duplicate_image_job_creator": False,
    }
