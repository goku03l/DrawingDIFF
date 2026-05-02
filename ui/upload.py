"""
ui/upload.py
Renders the two-column file-upload section and returns the uploaded files.
Supports: PNG, JPG, WEBP, TIFF, SVG, PDF
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import streamlit as st
from PIL import Image

from converters import ACCEPTED_TYPES, to_pil

# Human-readable format label shown in the UI
_FORMAT_HINT = "PNG · JPG · WEBP · TIFF · SVG · PDF"


def _label(text: str) -> None:
    st.markdown(
        f'<p style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
        f'letter-spacing:.06em;text-transform:uppercase;color:#6b7280 !important;'
        f'margin-bottom:4px">{text}</p>',
        unsafe_allow_html=True,
    )


def _format_badge() -> None:
    st.markdown(
        f'<p style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'letter-spacing:.05em;color:#4b5563 !important;margin-top:-4px;'
        f'margin-bottom:6px">{_FORMAT_HINT}</p>',
        unsafe_allow_html=True,
    )


def _preview(file) -> None:
    """Render a preview regardless of file type."""
    if file is None:
        return
    ext = file.name.rsplit(".", 1)[-1].lower()
    try:
        if ext in ("svg",):
            # Streamlit can render SVG directly as HTML
            file.seek(0)
            svg_data = file.read().decode("utf-8", errors="replace")
            file.seek(0)
            st.markdown(
                f'<div style="background:#16181c;border:1px solid #2a2d34;'
                f'border-radius:6px;padding:8px;text-align:center">'
                f'{svg_data}</div>',
                unsafe_allow_html=True,
            )
        else:
            # For raster + TIFF + PDF: convert to PIL then show as PNG
            img = to_pil(file)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), use_container_width=True)
    except Exception as e:
        st.warning(f"Preview unavailable: {e}")


def render_upload():
    """
    Render the upload widgets and return (f1, f2).
    Both values are None until the user selects files.
    """
    c1, c2 = st.columns(2)

    with c1:
        _label("Drawing 1 — Reference")
        _format_badge()
        f1 = st.file_uploader(
            "d1", type=ACCEPTED_TYPES,
            label_visibility="collapsed", key="f1",
        )
        _preview(f1)

    with c2:
        _label("Drawing 2 — Variant")
        _format_badge()
        f2 = st.file_uploader(
            "d2", type=ACCEPTED_TYPES,
            label_visibility="collapsed", key="f2",
        )
        _preview(f2)

    return f1, f2
