"""HTML pill navigation helpers for Naz Lab.

Streamlit's native st.tabs can be difficult to style consistently across
runtime versions. These helpers use query-parameter links, giving reliable
visible menu separation without relying on tab underline CSS.
"""

from __future__ import annotations

from html import escape
from urllib.parse import urlencode

import streamlit as st


def _query_dict() -> dict[str, str]:
    params: dict[str, str] = {}
    try:
        for key, value in st.query_params.items():
            if isinstance(value, list):
                params[key] = str(value[0]) if value else ""
            else:
                params[key] = str(value)
    except Exception:
        params = {}
    return params


def _href_for(key: str, option: str) -> str:
    params = _query_dict()
    params[key] = option
    return "?" + urlencode(params)


def render_nav(options: list[str], *, key: str, variant: str = "main") -> str:
    """Render a reliable HTML pill navigation row and return the selected option."""
    if not options:
        return ""
    params = _query_dict()
    selected = params.get(key, options[0])
    if selected not in options:
        selected = options[0]

    label = "MAIN MENU" if variant == "main" else "SECTION MENU"
    css_class = "naz-main-menu" if variant == "main" else "naz-sub-menu"
    items = []
    for option in options:
        active = " active" if option == selected else ""
        href = _href_for(key, option)
        items.append(f'<a class="naz-menu-pill{active}" href="{escape(href)}">{escape(option)}</a>')
    st.markdown(
        f'<div class="{css_class}-label">{label}</div>'
        f'<nav class="{css_class}" aria-label="{label}">' + "".join(items) + "</nav>",
        unsafe_allow_html=True,
    )
    return selected
