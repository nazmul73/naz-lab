"""Same-window navigation helpers for Naz Lab.

Uses Streamlit stateful controls instead of HTML links, so clicking a menu item
keeps the user in the same Colab/Streamlit window.
"""

from __future__ import annotations

import streamlit as st


def render_nav(options: list[str], *, key: str, variant: str = "main") -> str:
    """Render a same-window navigation control and return selected option."""
    if not options:
        return ""
    state_key = f"naz_nav_{key}"
    if state_key not in st.session_state or st.session_state[state_key] not in options:
        st.session_state[state_key] = options[0]

    css_class = "naz-main-menu-shell" if variant == "main" else "naz-sub-menu-shell"
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    try:
        selected = st.segmented_control(
            "Navigation",
            options,
            default=st.session_state[state_key],
            key=f"{state_key}_segmented",
            label_visibility="collapsed",
        )
    except Exception:
        selected = st.radio(
            "Navigation",
            options,
            index=options.index(st.session_state[state_key]),
            horizontal=True,
            key=f"{state_key}_radio",
            label_visibility="collapsed",
        )
    selected = selected or st.session_state[state_key]
    st.session_state[state_key] = selected
    st.markdown('</div>', unsafe_allow_html=True)
    return selected
