"""
ui/upload.py
Renders the two-column file-upload section and returns the uploaded files.
"""

import streamlit as st


def _label(text: str) -> None:
    st.markdown(
        f'<p style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
        f'letter-spacing:.06em;text-transform:uppercase;color:#6b7280 !important;'
        f'margin-bottom:4px">{text}</p>',
        unsafe_allow_html=True,
    )


def render_upload():
    """
    Render the upload widgets and return (f1, f2).
    Both values are None until the user selects files.
    """
    c1, c2 = st.columns(2)

    with c1:
        _label("Drawing 1 — Reference")
        f1 = st.file_uploader(
            "d1", type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed", key="f1",
        )
        if f1:
            st.image(f1, use_container_width=True)

    with c2:
        _label("Drawing 2 — Variant")
        f2 = st.file_uploader(
            "d2", type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed", key="f2",
        )
        if f2:
            st.image(f2, use_container_width=True)

    return f1, f2
