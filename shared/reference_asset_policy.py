"""Reference asset safety policy constants for Naz Lab."""

from __future__ import annotations

REFERENCE_ASSET_POLICY = (
    "Reference assets must be user-provided or explicitly authorized for the workflow. "
    "Do not use reference voice or face assets for misleading, deceptive, unauthorized, "
    "or impersonation-style output."
)

REFERENCE_ALLOWED_USE = [
    "user-provided voice reference for narration workflow",
    "explicitly authorized voice reference",
    "user-provided portrait/photo reference",
    "explicitly authorized portrait reference",
    "non-misleading delivery or style reference",
]

REFERENCE_DISALLOWED_USE = [
    "unauthorized celebrity voice or face cloning",
    "deceptive impersonation",
    "using a reference asset without permission",
    "pretending generated media is real when it is not",
    "misleading, scam, defamation, or manipulation use",
]

VOICE_REFERENCE_ALLOWED_EXTENSIONS = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
PORTRAIT_REFERENCE_ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

VOICE_REFERENCE_POLICY_FIELDS = {
    "reference_voice_path": "",
    "reference_voice_authorized": False,
    "reference_voice_notes": "",
    "reference_policy": "Reference voice requires user-provided or explicitly authorized audio.",
}

PORTRAIT_REFERENCE_POLICY_FIELDS = {
    "reference_image_path": "",
    "reference_image_authorized": False,
    "reference_image_notes": "",
    "reference_policy": "Reference image requires user-provided or explicitly authorized image.",
}

REFERENCE_MANAGER_UI_REQUIREMENTS = [
    "reference folder path",
    "upload area",
    "saved reference list",
    "selected reference path",
    "authorization checkbox",
    "notes field",
    "package preview",
    "warning against unauthorized use",
]


def is_allowed_reference_extension(filename: str, kind: str) -> bool:
    """Return True if filename extension is allowed for the reference asset kind."""
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    normalized = f".{suffix}" if suffix else ""
    if kind == "voice":
        return normalized in VOICE_REFERENCE_ALLOWED_EXTENSIONS
    if kind == "portrait":
        return normalized in PORTRAIT_REFERENCE_ALLOWED_EXTENSIONS
    return False
