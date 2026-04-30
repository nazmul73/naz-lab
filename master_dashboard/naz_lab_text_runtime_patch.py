"""Runtime fixes for Naz Lab Text panel language and fallback routing.

This module keeps the large Text panel intact and patches only the resolver and
fallback behavior used by the Streamlit runtime.
"""

from __future__ import annotations

import re

from master_dashboard import naz_lab_text_panel as text_panel

ENGLISH_TRUE_CRIME_TERMS = {
    "crime",
    "true crime",
    "unsolved",
    "mystery",
    "case",
    "story",
    "murder",
    "detective",
    "investigation",
}

BANGLA_CASUAL = {"হাই", "হ্যালো", "হেলো", "কেমন আছ", "কেমন আছো", "তুমি কেমন আছ", "তুমি কেমন আছো"}
ENGLISH_CASUAL = {"hi", "hello", "hey", "how are you", "who are you", "what are you", "thanks", "thank you", "ok", "okay", "test"}


def _clean(text: str) -> str:
    return " ".join(str(text or "").strip().split())


def _lower_clean(text: str) -> str:
    return _clean(text).lower().strip(" ?!.।")


def _has_bangla(text: str) -> bool:
    return any("\u0980" <= ch <= "\u09FF" for ch in str(text or ""))


def _is_casual(text: str) -> bool:
    clean = _clean(text)
    lower = _lower_clean(clean)
    if lower in ENGLISH_CASUAL or clean.strip(" ?!.।") in BANGLA_CASUAL:
        return True
    word_count = len(re.findall(r"[\w\u0980-\u09FF]+", clean))
    return word_count <= 4 and clean.endswith(("?", "।"))


def _detect_content_mode(text: str, selected_mode: str) -> str:
    lower = _lower_clean(text)
    if any(term in lower for term in ENGLISH_TRUE_CRIME_TERMS):
        if "script" in lower or "reel" in lower or "video" in lower:
            return "Viral Script Writer"
        return "Story Writer"
    return selected_mode


def patched_resolve_effective_mode_language(selected_mode: str, language: str, topic: str) -> tuple[str, str, str]:
    has_bangla = _has_bangla(topic)
    if _is_casual(topic):
        return "General Chat", "Bangla" if has_bangla else "English", "casual_chat_detected"

    adjusted_mode = _detect_content_mode(topic, selected_mode)
    policy = text_panel.MODE_POLICY.get(adjusted_mode, text_panel.MODE_POLICY["Free Writer"])
    effective_mode = str(policy["internal_mode"])

    # English-only input should stay English even when the UI default language is Bangla.
    effective_language = "Bangla" if has_bangla else "English"
    reason = "content_intent_detected" if adjusted_mode != selected_mode else "selected_mode"
    return effective_mode, effective_language, reason


def patched_fallback_output(mode: str, topic: str, language: str) -> str:
    clean = _clean(topic)
    lower = _lower_clean(clean)
    has_bangla = _has_bangla(clean)

    if mode == "General Chat":
        if has_bangla:
            if lower in {"হাই", "হ্যালো", "হেলো"}:
                return "হাই! কীভাবে সাহায্য করতে পারি?"
            if "কেমন আছ" in clean:
                return "আমি ভালো আছি। আপনি কী নিয়ে কাজ করতে চান?"
            return f"আপনি লিখেছেন: {clean}\n\nআমি বুঝেছি। এখন আপনি কী ধরনের আউটপুট চান?"
        if lower in {"hi", "hello", "hey"}:
            return "Hi! How can I help you today?"
        if lower == "how are you":
            return "I'm doing well, thanks for asking. How can I help you today?"
        if lower in {"who are you", "what are you"}:
            return "I'm Naz Lab's AI assistant inside this dashboard. I can help with text, scripts, prompts, image jobs, voice jobs, and content workflow."
        return f"I understand: {clean}\n\nHow would you like me to help with this?"

    if language == "English":
        if mode == "Story Writer":
            return (
                "Yes. Here is a safe unsolved true crime story framework you can use:\n\n"
                "Title: The Last Light in the Window\n\n"
                "A quiet neighborhood was shaken when an adult resident vanished after leaving behind an ordinary evening routine: a half-finished cup of tea, a locked front door, and one light still glowing upstairs. Investigators found no clear sign of forced entry, and the timeline quickly became the most troubling part of the case.\n\n"
                "Neighbors remembered small details that did not fully match. One person heard footsteps near the gate. Another saw a car pause outside the house for less than a minute. None of it was enough to prove what happened.\n\n"
                "Years later, the case remains unsolved because every clue points in a different direction. Was it a planned disappearance, a familiar person, or a chance encounter that turned dangerous?"
            )
        if mode in {"Viral Script Writer", "YouTube Script"}:
            return (
                "Hook: An ordinary evening became a mystery that still has no clear answer.\n\n"
                "Body: The person was last seen following a normal routine. No obvious break-in, no simple motive, and no confirmed suspect. The case became confusing because every witness remembered something slightly different.\n\n"
                "Psychology line: Unsolved cases stay powerful because the human brain keeps searching for closure when the facts refuse to line up.\n\n"
                "CTA: What detail would you investigate first?"
            )
        if mode == "Caption Writer":
            return "An ordinary night, a missing person, and a case that still leaves more questions than answers. What clue would you focus on first?"
        return f"Yes. I can help with that. Here is a clean starting point:\n\n{clean}\n\nTell me whether you want it as a story, reel script, caption, or image prompt."

    return text_panel.template_output(mode, topic)


# Apply monkey patch before exposing render_text_panel.
text_panel.resolve_effective_mode_language = patched_resolve_effective_mode_language
text_panel.fallback_output = patched_fallback_output
render_text_panel = text_panel.render_text_panel
