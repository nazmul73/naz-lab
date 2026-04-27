"""Global language policy for Naz Lab.

Naz Lab is Bangla-first by default. English remains supported and is the
project default for English-specific presets such as True Noir Tales and
ToolFlow. Other languages are optional.
"""

from __future__ import annotations

GLOBAL_LANGUAGE_POLICY = {
    "priority": ["Bangla", "English", "Other optional"],
    "default_language": "Bangla",
    "english_project_presets": ["True Noir Tales", "ToolFlow"],
    "primary_regional_bangla": "Rangpur/Nilphamari/North Bengal",
    "secondary_regional_bangla": ["Dhakaiya", "Chattogram", "Sylhet", "Noakhali/Comilla"],
    "bangla_requirements": [
        "natural spoken Bangla",
        "Facebook-ready",
        "netizen-friendly",
        "voiceover-ready",
        "simple and human, not stiff textbook Bangla",
    ],
    "english_requirements": [
        "clean",
        "practical",
        "ready-to-use",
        "default only for selected English projects or when requested",
    ],
}

BANGLA_FIRST_NOTE_BN = (
    "Naz Lab default হবে Bangla-first। বেশির ভাগ content বাংলায় হবে। "
    "English থাকবে selected English project বা user request অনুযায়ী। "
    "আঞ্চলিক বাংলা লাগলে primary default: রংপুর/নীলফামারী/উত্তরবঙ্গ।"
)

BANGLA_FIRST_NOTE_EN = (
    "Naz Lab is Bangla-first by default. English is supported as a second language "
    "and remains the default for selected English projects such as True Noir Tales "
    "and ToolFlow. Other languages are optional."
)
