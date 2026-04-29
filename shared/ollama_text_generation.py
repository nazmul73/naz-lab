"""Ollama text generation helpers for Naz Lab.

This module centralizes the model-specific prompt format, Bangla-friendly token
limits, and approved fallback chain for Text Builder generation.
"""

from __future__ import annotations

import requests

from shared.model_policy import MINIMUM_CPU_TEXT_MODEL, RECOMMENDED_TEXT_MODEL, normalize_text_model

OLLAMA_GENERATE_ENDPOINT = "http://localhost:11434/api/generate"
REQUEST_TIMEOUT_SECONDS = 420

BANGLA_LENGTH_TOKEN_LIMITS = {"Short": 600, "Medium": 1200, "Long": 3000}
ENGLISH_LENGTH_TOKEN_LIMITS = {"Short": 450, "Medium": 900, "Long": 1800}


def user_requested_bangla(text: str, language: str) -> bool:
    if language != "English":
        return True
    return any("\u0980" <= ch <= "\u09FF" for ch in text)


def get_token_limit(language: str, length: str, user_prompt: str = "") -> int:
    if user_requested_bangla(user_prompt, language):
        return BANGLA_LENGTH_TOKEN_LIMITS.get(length, BANGLA_LENGTH_TOKEN_LIMITS["Medium"])
    return ENGLISH_LENGTH_TOKEN_LIMITS.get(length, ENGLISH_LENGTH_TOKEN_LIMITS["Medium"])


def build_system_instruction(mode: str, language: str, length: str, bangla_safe_mode: bool) -> str:
    lang_rule = "Write in natural, simple Bangla." if language != "English" else "Write in clear English."
    if language == "Mixed Bangla-English":
        lang_rule = "Write in natural Bangla with simple English terms only where useful."
    safe_rule = "Bangla Safe Mode is ON: avoid broken, literal, machine-translated Bangla. Use natural spoken Bangla and complete sections." if bangla_safe_mode else ""
    structure = {
        "General Chat": "Reply conversationally and directly. Do not force a content template.",
        "Free Writer": "Write a complete ready-to-use draft with clear paragraphs.",
        "Story Writer": "Use sections: Title, Setup, Main Event, Turning Point, Ending, Question CTA.",
        "Viral Script Writer": "Use sections: Title, Hook, Voiceover, On-screen text, Caption, CTA. Make it complete.",
        "YouTube Script": "Use sections: Title, Intro Hook, Main Points, Example, Closing CTA. Make it long enough for the requested length.",
        "Caption Writer": "Write Caption 1, Caption 2, Caption 3 with practical variation.",
        "Prompt Improver": "Write one polished visual prompt and one negative prompt. Return final prompt text only.",
    }.get(mode, "Write the final output directly.")
    return "\n".join([
        "You are Naz Lab Text Workstation.",
        lang_rule,
        safe_rule,
        structure,
        f"Length setting: {length}. Use enough detail; do not stop early.",
        "Return final output only. Do not repeat these instructions.",
    ]).strip()


def build_prompt_for_model(model: str, system_instruction: str, user_prompt: str) -> tuple[str, list[str]]:
    model_name = model.lower()
    if model_name.startswith("gemma"):
        prompt = (
            "<start_of_turn>user\n"
            f"{system_instruction}\n\nUSER REQUEST:\n{user_prompt}"
            "<end_of_turn>\n<start_of_turn>model\n"
        )
        return prompt, ["<end_of_turn>", "<start_of_turn>user"]
    if model_name.startswith("qwen"):
        prompt = (
            f"<|im_start|>system\n{system_instruction}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        return prompt, ["<|im_end|>", "<|im_start|>user", "INSTRUCTION:", "TASK:"]
    prompt = f"{system_instruction}\n\nUSER REQUEST:\n{user_prompt}\n\nFINAL OUTPUT:\n"
    return prompt, ["INSTRUCTION:", "TASK:"]


def clean_model_output(text: str) -> str:
    for marker in ["<|im_end|>", "<|im_start|>", "<end_of_turn>", "<start_of_turn>"]:
        text = text.replace(marker, "")
    return text.strip()


def _call_single_model(user_prompt: str, model: str, mode: str, language: str, length: str, bangla_safe_mode: bool) -> str:
    system_instruction = build_system_instruction(mode, language, length, bangla_safe_mode)
    prompt, stop = build_prompt_for_model(model, system_instruction, user_prompt)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": get_token_limit(language, length, user_prompt),
            "temperature": 0.24,
            "top_p": 0.9,
            "repeat_penalty": 1.12,
            "stop": stop,
        },
    }
    response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return clean_model_output(str(response.json().get("response", "")))


def call_ollama(user_prompt: str, model: str, mode: str, language: str, length: str, bangla_safe_mode: bool) -> str:
    """Generate text with model-specific prompt format and a safe fallback chain."""
    selected = normalize_text_model(model)
    fallback_chain = [selected]
    for fallback in [RECOMMENDED_TEXT_MODEL, MINIMUM_CPU_TEXT_MODEL]:
        if fallback not in fallback_chain:
            fallback_chain.append(fallback)
    last_error: Exception | None = None
    for candidate in fallback_chain:
        try:
            output = _call_single_model(user_prompt, candidate, mode, language, length, bangla_safe_mode)
            if output:
                return output
        except Exception as exc:  # caller already has template fallback handling
            last_error = exc
            continue
    if last_error:
        raise last_error
    return ""


def generation_policy_status() -> dict[str, object]:
    return {
        "bangla_length_token_limits": BANGLA_LENGTH_TOKEN_LIMITS,
        "english_length_token_limits": ENGLISH_LENGTH_TOKEN_LIMITS,
        "prompt_formats": {"gemma": "Gemma turn format", "qwen": "ChatML", "other": "generic instruction prompt"},
        "fallback_chain": [RECOMMENDED_TEXT_MODEL, MINIMUM_CPU_TEXT_MODEL],
    }
