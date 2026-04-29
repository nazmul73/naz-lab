"""Button-based navigation helpers for Naz Lab.

Streamlit's native st.tabs can be difficult to style consistently across
runtime versions. These helpers use session-state + buttons, giving visible
separation without relying on tab underline CSS.
"""

from __future__ import annotations

import streamlit as st


def render_nav(options: list[str], *, key: str, variant: str = "main") -> str:
    """Render a button-based navigation row and return the selected option."""
    if not options:
        return ""
    if key not in st.session_state or st.session_state[key] not in options:
        st.session_state[key] = options[0]

    if variant == "main":
        st.markdown('<div class="naz-main-menu-label">MAIN MENU</div>', unsafe_allow_html=True)
        st.markdown('<div class="naz-main-menu-wrap">', unsafe_allow_html=True)
    else:
        st.markdown('<div class="naz-sub-menu-label">SECTION MENU</div>', unsafe_allow_html=True)
        st.markdown('<div class="naz-sub-menu-wrap">', unsafe_allow_html=True)

    cols = st.columns(len(options), gap="small")
    for index, option in enumerate(options):
        selected = st.session_state[key] == option
        with cols[index]:
            button_type = "primary" if selected else "secondary"
            if st.button(option, key=f"{key}_{option}", use_container_width=True, type=button_type):
                st.session_state[key] = option
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    return st.session_state[key]
