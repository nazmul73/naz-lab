"""Runtime fixes for Naz Lab Text panel language and fallback routing.

This module keeps the large Text panel intact and patches the resolver/fallback
behavior used by the Streamlit runtime. Fallback output must be useful even when
Ollama is unavailable, because Colab model availability can vary.
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

BANGLA_TRUE_CRIME_TERMS = {
    "ক্রাইম",
    "অপরাধ",
    "রহস্য",
    "অমীমাংসিত",
    "কেস",
    "গল্প",
    "তদন্ত",
}

BANGLA_CASUAL = {
    "হাই",
    "হ্যালো",
    "হেলো",
    "কেমন আছ",
    "কেমন আছো",
    "তুমি কেমন আছ",
    "তুমি কেমন আছো",
    "তোমার নাম কি",
    "তোমার নাম কী",
    "তুমি কে",
    "তুমি কে?",
    "তুমি কি",
    "তুমি কী",
}
ENGLISH_CASUAL = {
    "hi",
    "hello",
    "hey",
    "how are you",
    "who are you",
    "what are you",
    "what is your name",
    "your name",
    "thanks",
    "thank you",
    "ok",
    "okay",
    "test",
}


def _clean(text: str) -> str:
    return " ".join(str(text or "").strip().split())


def _strip_punctuation(text: str) -> str:
    return _clean(text).strip(" ?!.,।॥:;\n\t")


def _lower_clean(text: str) -> str:
    return _strip_punctuation(text).lower()


def _has_bangla(text: str) -> bool:
    return any("\u0980" <= ch <= "\u09FF" for ch in str(text or ""))


def _is_casual(text: str) -> bool:
    clean = _clean(text)
    stripped = _strip_punctuation(clean)
    lower = stripped.lower()
    if lower in ENGLISH_CASUAL or stripped in BANGLA_CASUAL:
        return True
    word_count = len(re.findall(r"[\w\u0980-\u09FF]+", clean))
    return word_count <= 5 and clean.endswith(("?", "??", "।"))


def _respect_selected_language(language: str, topic: str) -> str:
    if language in {"Bangla", "English", "Mixed Bangla-English"}:
        return language
    return "Bangla" if _has_bangla(topic) else "English"


def _detect_content_mode(text: str, selected_mode: str) -> str:
    lower = _lower_clean(text)
    if selected_mode not in {"General Chat", "Free Writer"}:
        return selected_mode
    if any(term in lower for term in ENGLISH_TRUE_CRIME_TERMS) or any(term in text for term in BANGLA_TRUE_CRIME_TERMS):
        if "script" in lower or "reel" in lower or "video" in lower or "স্ক্রিপ্ট" in text or "রিল" in text:
            return "Viral Script Writer"
        return "Story Writer"
    return selected_mode


def patched_resolve_effective_mode_language(selected_mode: str, language: str, topic: str) -> tuple[str, str, str]:
    if _is_casual(topic) and selected_mode in {"General Chat", "Free Writer"}:
        return "General Chat", "Bangla" if _has_bangla(topic) else "English", "casual_chat_detected"

    adjusted_mode = _detect_content_mode(topic, selected_mode)
    policy = text_panel.MODE_POLICY.get(adjusted_mode, text_panel.MODE_POLICY["Free Writer"])
    effective_mode = str(policy["internal_mode"])
    effective_language = _respect_selected_language(language, topic)
    reason = "content_intent_detected" if adjusted_mode != selected_mode else "selected_mode"
    return effective_mode, effective_language, reason


def _bangla_general_reply(clean: str) -> str:
    lower = _lower_clean(clean)
    if lower in {"হাই", "হ্যালো", "হেলো"}:
        return "হাই! কীভাবে সাহায্য করতে পারি?"
    if "নাম" in clean:
        return "আমি Naz Lab-এর AI সহকারী। Text, script, caption, image prompt, voice job আর content workflow তৈরি করতে সাহায্য করি।"
    if "কে" in clean or "কি" in clean or "কী" in clean:
        return "আমি Naz Lab-এর AI সহকারী। আপনি চাইলে আমাকে দিয়ে লেখা, গল্প, স্ক্রিপ্ট, ক্যাপশন বা prompt তৈরি করাতে পারেন।"
    if "কেমন আছ" in clean:
        return "আমি ভালো আছি। আপনি কী নিয়ে কাজ করতে চান?"
    return f"আমি বুঝেছি: {clean}\n\nএটা নিয়ে আপনি কী ধরনের লেখা চান—গল্প, স্ক্রিপ্ট, ক্যাপশন, নাকি image prompt?"


def _english_general_reply(clean: str) -> str:
    lower = _lower_clean(clean)
    if lower in {"hi", "hello", "hey"}:
        return "Hi! How can I help you today?"
    if lower == "how are you":
        return "I'm doing well, thanks for asking. How can I help you today?"
    if lower in {"who are you", "what are you", "what is your name", "your name"}:
        return "I'm Naz Lab's AI assistant. I can help with text, scripts, captions, image prompts, voice jobs, and content workflow."
    return f"I understand: {clean}\n\nWould you like this as a story, script, caption, image prompt, or content plan?"


def _bangla_story(clean: str) -> str:
    return (
        f"শিরোনাম: অমীমাংসিত ছায়া\n\n"
        f"{clean}—এই বিষয়টি ঘিরে গল্পটা শুরু হয় এক সাধারণ সন্ধ্যা থেকে। সবকিছু স্বাভাবিক ছিল, কিন্তু কয়েকটি ছোট ঘটনা পরে বড় রহস্যে পরিণত হয়। একজন প্রাপ্তবয়স্ক মানুষ হঠাৎ এমনভাবে হারিয়ে যায় বা এমন এক ঘটনার মধ্যে জড়িয়ে পড়ে, যার সরল ব্যাখ্যা কেউ খুঁজে পায় না।\n\n"
        "প্রতিবেশীরা কিছু শব্দ শুনেছিল, কেউ একজন অচেনা ছায়া দেখেছিল, আর সময়ের হিসাব মিলছিল না। তদন্তকারীরা কয়েকটি সূত্র পেলেও কোনো সূত্রই পুরো সত্যের দরজা খুলতে পারেনি।\n\n"
        "আজও প্রশ্ন রয়ে গেছে—ঘটনাটি কি পরিকল্পিত ছিল, পরিচিত কেউ জড়িত ছিল, নাকি এক অপ্রত্যাশিত মুহূর্ত সবকিছু বদলে দিয়েছিল?"
    )


def _english_story(clean: str) -> str:
    return (
        "Title: The Question No One Could Answer\n\n"
        f"The story begins with a simple request: {clean}\n\n"
        "An ordinary evening turned into a mystery when small details stopped making sense. A light was left on, a routine was interrupted, and the last known moments created more questions than answers.\n\n"
        "Investigators found fragments of a timeline, but every witness remembered something slightly different. One person heard movement near the gate. Another noticed a car slow down and leave. None of it was enough to close the case.\n\n"
        "Years later, the case remains unsolved because the strongest clue is also the most troubling one: someone may know exactly what happened, but has never spoken."
    )


def _bangla_script(clean: str) -> str:
    return (
        f"Hook: {clean}—এই প্রশ্নটাই পুরো ঘটনাকে রহস্যময় করে তোলে।\n\n"
        "Body: শুরুতে ঘটনাটা সাধারণ মনে হয়েছিল। কিন্তু সময়, সাক্ষ্য আর ছোট ছোট সূত্র মিলিয়ে দেখা যায়—কিছু একটা ঠিক নেই। প্রত্যেক তথ্য যেন আরেকটা নতুন প্রশ্ন তৈরি করে।\n\n"
        "Psychology line: মানুষ রহস্যে আটকে যায় কারণ অসম্পূর্ণ তথ্য আমাদের মস্তিষ্ককে closure খুঁজতে বাধ্য করে।\n\n"
        "CTA: আপনার মনে হয় কোন সূত্রটা আগে খতিয়ে দেখা উচিত?"
    )


def _english_script(clean: str) -> str:
    return (
        f"Hook: {clean}\n\n"
        "Body: At first, the case looked ordinary. Then the timeline started to break apart. A missing detail, a quiet witness, and one unanswered question kept the mystery alive.\n\n"
        "Psychology line: Unsolved stories stay powerful because the mind keeps searching for closure.\n\n"
        "CTA: What detail would you investigate first?"
    )


def _bangla_caption(clean: str) -> str:
    return f"একটা ছোট প্রশ্ন, কিন্তু তার ভেতরে লুকিয়ে থাকতে পারে পুরো গল্পের সবচেয়ে বড় রহস্য: {clean}\n\nআপনি হলে কোন দিকটা আগে খতিয়ে দেখতেন?"


def _english_caption(clean: str) -> str:
    return f"One small question can hold the biggest mystery: {clean}\n\nWhat detail would you look at first?"


def _bangla_prompt(clean: str) -> str:
    return (
        f"বাংলাদেশের বাস্তব পরিবেশে cinematic realistic scene, বিষয়: {clean}, adult Bangladeshi subject, emotional tension, natural lighting, detailed background, social media ready composition, 1:1 square, high detail\n\n"
        "Negative prompt: no fake logo, no watermark, no distorted face"
    )


def _english_prompt(clean: str) -> str:
    return (
        f"Cinematic realistic visual set in Bangladesh, theme: {clean}, adult Bangladeshi subject, emotional tension, natural lighting, detailed environment, premium social media composition, 1:1 square, high detail\n\n"
        "Negative prompt: no fake logo, no watermark, no distorted face"
    )


def _bangla_free(clean: str) -> str:
    return f"{clean}\n\nএই বিষয়টি নিয়ে লেখা শুরু করা যায় একটি সহজ, মানবিক পর্যবেক্ষণ দিয়ে। মূল ভাবনাটি পরিষ্কার রাখুন, তারপর ধাপে ধাপে ঘটনা, অনুভূতি এবং প্রশ্ন যোগ করুন। এতে লেখাটি স্বাভাবিক, পড়ার মতো এবং ব্যবহারযোগ্য হবে।"


def _english_free(clean: str) -> str:
    return f"{clean}\n\nA strong way to develop this is to start with the main idea, then add context, emotion, and one clear question. That keeps the writing focused, readable, and useful."


def patched_fallback_output(mode: str, topic: str, language: str) -> str:
    clean = _clean(topic)
    is_bangla = language == "Bangla" or (language == "Mixed Bangla-English" and _has_bangla(clean))

    if mode == "General Chat":
        return _bangla_general_reply(clean) if is_bangla else _english_general_reply(clean)
    if mode == "Story Writer":
        return _bangla_story(clean) if is_bangla else _english_story(clean)
    if mode in {"Viral Script Writer", "YouTube Script"}:
        return _bangla_script(clean) if is_bangla else _english_script(clean)
    if mode == "Caption Writer":
        return _bangla_caption(clean) if is_bangla else _english_caption(clean)
    if mode == "Prompt Improver":
        return _bangla_prompt(clean) if is_bangla else _english_prompt(clean)
    return _bangla_free(clean) if is_bangla else _english_free(clean)


# Apply monkey patch before exposing render_text_panel.
text_panel.resolve_effective_mode_language = patched_resolve_effective_mode_language
text_panel.fallback_output = patched_fallback_output
render_text_panel = text_panel.render_text_panel
