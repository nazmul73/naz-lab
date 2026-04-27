"""Reusable Bangla quality rules for Naz Lab."""

from __future__ import annotations

BANGLA_QUALITY_ENGINE = {
    "priority": ["Bangla", "English", "Other optional"],
    "core_rule": "Bangla must be natural, spoken, Facebook-ready, netizen-friendly, voiceover-ready, simple, human, and not stiff textbook Bangla.",
    "primary_regional_tone": "Rangpur/Nilphamari/North Bengal",
    "secondary_regional_tones": ["Dhakaiya", "Chattogram", "Sylhet", "Noakhali/Comilla"],
    "voiceover_rules": [
        "one idea per sentence",
        "short clauses",
        "clear pause points",
        "easy to say out loud",
        "avoid long tangled sentences",
        "avoid robotic phrasing",
    ],
    "facebook_rules": [
        "conversational",
        "social-friendly",
        "clear emotional hook",
        "ends with a question when useful",
        "no fake urgency",
        "no misleading clickbait",
    ],
    "avoid_words_or_styles": [
        "অতএব",
        "পরিশেষে",
        "নিম্নোক্ত",
        "উক্ত বিষয়",
        "over-formal newsreader tone",
        "stiff textbook Bangla",
    ],
}

BANGLA_PROMPT_RULE = (
    "বাংলা হবে natural spoken Bangla, Facebook-ready, netizen-friendly, "
    "voiceover-ready, simple, human, and not stiff textbook Bangla. "
    "Regional tone needed হলে default হবে Rangpur/Nilphamari/North Bengal flavor, lightly and naturally."
)

TRUE_NOIR_BANGLA_RULE = (
    "True Noir Tales Bangla হলে suspenseful but restrained, simple, emotional, factual, "
    "no gore details, no dead body description, no visible wound language, and end with a question when useful."
)

TOOLFLOW_BANGLA_RULE = (
    "ToolFlow Bangla হলে practical, clean, useful, beginner-friendly, non-hype, "
    "and no fake income claims."
)
