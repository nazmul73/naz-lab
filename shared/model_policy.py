"""Central model policy for Naz Lab text generation.

This module prevents weak fallback models from being presented as normal text
models in the dashboard. The policy is intentionally small and dependency-free
so panels, launchers, and backend checks can import it safely.
"""

from __future__ import annotations

from typing import Iterable

MINIMUM_CPU_TEXT_MODEL = "qwen2.5:1.5b"
RECOMMENDED_TEXT_MODEL = "gemma2:2b"
OPTIONAL_TEXT_MODEL = "qwen2.5:3b"

ALLOWED_TEXT_MODELS = [RECOMMENDED_TEXT_MODEL, MINIMUM_CPU_TEXT_MODEL, OPTIONAL_TEXT_MODEL]
BLOCKED_TEXT_MODELS = {
    "qwen2.5:0.5b": "Too weak for professional Bangla output; use gemma2:2b or qwen2.5:1.5b.",
    "tinyllama": "Too weak for professional Bangla output; use gemma2:2b or qwen2.5:1.5b.",
}


def is_text_model_allowed(model: str) -> bool:
    return model in ALLOWED_TEXT_MODELS


def normalize_text_model(model: str | None) -> str:
    """Return a safe model for Text Builder generation."""
    if model and is_text_model_allowed(model):
        return model
    return RECOMMENDED_TEXT_MODEL


def filter_allowed_text_models(models: Iterable[str] | None = None) -> list[str]:
    """Keep only policy-approved text models while preserving order."""
    source = list(models or ALLOWED_TEXT_MODELS)
    result: list[str] = []
    for model in source:
        if model in ALLOWED_TEXT_MODELS and model not in result:
            result.append(model)
    for model in ALLOWED_TEXT_MODELS:
        if model not in result:
            result.append(model)
    return result


def blocked_model_reason(model: str) -> str:
    return BLOCKED_TEXT_MODELS.get(model, "Model is not approved for Text Builder generation.")


def model_policy_status() -> dict[str, object]:
    return {
        "recommended_text_model": RECOMMENDED_TEXT_MODEL,
        "minimum_cpu_text_model": MINIMUM_CPU_TEXT_MODEL,
        "allowed_text_models": ALLOWED_TEXT_MODELS,
        "blocked_text_models": BLOCKED_TEXT_MODELS,
    }
