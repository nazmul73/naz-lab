"""Lightweight backend validation helpers for Naz Lab.

Future backend adapters should call these helpers before running any generation.
No heavy dependencies are imported here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from shared.backend_schema import (
    BACKEND_STATUS,
    OUTPUT_FIELD_BY_KIND,
    REQUIRED_FIELDS_BY_KIND,
    BackendValidationResult,
    infer_backend_kind_from_path,
    normalize_backend_kind,
)
from shared.reference_asset_policy import (
    REFERENCE_ASSET_POLICY,
    is_allowed_reference_extension,
)


def validate_required_fields(package: dict[str, Any], kind: str) -> list[str]:
    """Return missing required field names for a package kind."""

    backend_kind = normalize_backend_kind(kind)
    missing: list[str] = []
    for field in REQUIRED_FIELDS_BY_KIND.get(backend_kind, []):
        value = package.get(field)
        if value is None or value == "":
            missing.append(field)
    return missing


def validate_status(package: dict[str, Any]) -> list[str]:
    """Return validation messages for package status fields."""

    status = str(package.get("backend_status", package.get("status", "draft")))
    if status not in BACKEND_STATUS:
        return [f"Unsupported backend status: {status}"]
    return []


def validate_output_path(package: dict[str, Any], kind: str) -> list[str]:
    """Return warnings for missing output path metadata.

    Missing output path is a warning, not a hard block, because many current
    Naz Lab packages are planning packages and do not generate outputs yet.
    """

    backend_kind = normalize_backend_kind(kind)
    field = OUTPUT_FIELD_BY_KIND.get(backend_kind)
    if not field:
        return []
    if package.get(field) or package.get("suggested_output_path") or package.get("audio_output_path"):
        return []
    return [f"No output path metadata found for {backend_kind} backend."]


def validate_voice_reference(package: dict[str, Any]) -> list[str]:
    """Return blocking messages for unsafe voice reference use."""

    voice_mode = str(package.get("voice_mode", ""))
    reference_path = str(package.get("reference_voice_path", "")).strip()
    authorized = bool(package.get("reference_voice_authorized", package.get("clone_authorized", False)))

    if "reference voice" not in voice_mode.lower() and not reference_path:
        return []

    messages: list[str] = []
    if not reference_path:
        messages.append("Reference voice path is required for reference voice backend use.")
    elif not is_allowed_reference_extension(Path(reference_path).name, "voice"):
        messages.append("Reference voice extension is not allowed.")
    if reference_path and not authorized:
        messages.append("Reference voice is not authorized. Backend must not use it.")
    return messages


def validate_portrait_reference(package: dict[str, Any]) -> list[str]:
    """Return blocking messages for unsafe portrait reference use."""

    portrait_type = str(package.get("portrait_type", ""))
    face_policy = str(package.get("face_policy", ""))
    reference_path = str(package.get("reference_image_path", "")).strip()
    authorized = bool(package.get("reference_image_authorized", False))

    reference_requested = (
        "reference" in portrait_type.lower()
        or "reference" in face_policy.lower()
        or bool(reference_path)
    )
    if not reference_requested:
        return []

    messages: list[str] = []
    if not reference_path:
        messages.append("Reference image path is required for reference portrait backend use.")
    elif not is_allowed_reference_extension(Path(reference_path).name, "portrait"):
        messages.append("Reference image extension is not allowed.")
    if reference_path and not authorized:
        messages.append("Reference image is not authorized. Backend must not use it as identity/face reference.")
    if not package.get("no_misleading_identity_claim", False):
        messages.append("Missing no_misleading_identity_claim metadata for portrait reference backend use.")
    return messages


def validate_reference_policy(package: dict[str, Any], kind: str) -> list[str]:
    """Return blocking messages for reference policy violations."""

    backend_kind = normalize_backend_kind(kind)
    messages: list[str] = []
    if backend_kind == "voice":
        messages.extend(validate_voice_reference(package))
    if backend_kind == "portrait":
        messages.extend(validate_portrait_reference(package))

    if messages and not package.get("reference_policy"):
        messages.append(f"Missing reference policy metadata: {REFERENCE_ASSET_POLICY}")
    return messages


def validate_backend_package(package: dict[str, Any], kind: str | None = None, source_path: str | Path | None = None) -> BackendValidationResult:
    """Validate a future backend package without running any heavy backend."""

    backend_kind = normalize_backend_kind(kind or str(package.get("backend_kind", "")) or infer_backend_kind_from_path(source_path or ""))
    messages: list[str] = []
    warnings: list[str] = []

    missing = validate_required_fields(package, backend_kind)
    if missing:
        messages.append("Missing required fields: " + ", ".join(missing))

    messages.extend(validate_status(package))
    messages.extend(validate_reference_policy(package, backend_kind))
    warnings.extend(validate_output_path(package, backend_kind))

    ok = not messages
    return BackendValidationResult(
        ok=ok,
        status="ready_for_backend" if ok else "blocked",
        messages=messages or ["Package passed lightweight backend validation."],
        warnings=warnings,
    )
