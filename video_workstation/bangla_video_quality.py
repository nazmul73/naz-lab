"""Bangla video quality rules for Naz Lab Video Workstation."""

BANGLA_VIDEO_RULE = (
    "Bangla video package must be natural spoken Bangla, Facebook-ready, netizen-friendly, "
    "voiceover-ready, subtitle-friendly, simple, human, and not stiff textbook Bangla."
)

BANGLA_SUBTITLE_RULES = [
    "Use short subtitle lines.",
    "Keep each subtitle easy to read on mobile.",
    "Avoid long complex sentence blocks.",
    "Use natural spoken Bangla, not formal textbook phrasing.",
    "Make subtitle breaks match voiceover pauses.",
]

BANGLA_SCENE_RULES = [
    "First 3 seconds must have a clear hook.",
    "Each scene should carry one idea.",
    "Use natural Bangladeshi context for general Naz Lab content.",
    "Urban and rural Bangladesh are both allowed.",
    "For women, no sindoor unless explicitly requested.",
]

REGIONAL_VIDEO_RULES = {
    "Rangpur/Nilphamari": "Default regional flavor. Use light North Bengal tone naturally, especially in General Bangla videos.",
    "Dhaka": "Urban casual tone, faster and social-friendly. Use only when requested.",
    "Chattogram": "Readable light Chattogram flavor. Use only when requested.",
    "Sylhet": "Readable light Sylheti influence. Use only when requested.",
    "Noakhali/Comilla": "Conversational regional flavor without caricature. Use only when requested.",
}

TRUE_NOIR_VIDEO_BANGLA_RULE = (
    "For True Noir Tales Bangla video: suspenseful but restrained, adult-focused, no gore, "
    "no dead body, no visible wounds, no sensational violence, and end with a question when useful."
)

TOOLFLOW_VIDEO_BANGLA_RULE = (
    "For ToolFlow Bangla video: practical explainer flow, clean steps, non-hype, no fake income claims, "
    "and clear value delivery."
)

CAPCUT_BANGLA_EDIT_RULE = (
    "For CapCut/editor workflow: keep Bangla subtitles readable, use simple cuts, match subtitle breaks to voiceover, "
    "avoid overusing effects, and keep the final frame clear for CTA."
)
