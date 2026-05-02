"""
ui/overview.py
Renders the summary metrics row, annotated drawing overview,
and the "identical aspects" pill strip.
"""

import streamlit as st
from PIL import Image

from image_utils import annotate_image, to_png


def render_metrics(diffs: list, total: int) -> None:
    major    = sum(1 for d in diffs if d.get("severity") == "major")
    moderate = sum(1 for d in diffs if d.get("severity") == "moderate")
    minor    = sum(1 for d in diffs if d.get("severity") == "minor")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Differences", total)
    m2.metric("🔴 Major",    major)
    m3.metric("🟡 Moderate", moderate)
    m4.metric("🔵 Minor",    minor)


def render_summary_card(summary: str) -> None:
    if not summary:
        return
    st.markdown(
        f'<div style="background:#16181c;border:1px solid #2a2d34;border-radius:8px;'
        f'padding:1rem 1.25rem;margin:.75rem 0 1.25rem;color:#9ca3af !important;'
        f'font-size:13px;line-height:1.7">{summary}</div>',
        unsafe_allow_html=True,
    )


def render_annotated_overview(
    img1: Image.Image,
    img2: Image.Image,
    diffs: list,
    selected_id: int | None,
) -> None:
    if not diffs:
        return

    st.markdown("### 🗺️ Annotated Overview")
    st.caption(
        "Tight bounding boxes — selected row glows brighter.  "
        "Colors: 🔴 Major  🟡 Moderate  🔵 Minor"
    )

    def _col_label(text: str) -> None:
        st.markdown(
            f'<p style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
            f'letter-spacing:.06em;text-transform:uppercase;color:#6b7280 !important">'
            f'{text}</p>',
            unsafe_allow_html=True,
        )

    a1 = annotate_image(img1, diffs, "d1", selected_id)
    a2 = annotate_image(img2, diffs, "d2", selected_id)

    ov1, ov2 = st.columns(2)
    with ov1:
        _col_label("Drawing 1 — Reference")
        st.image(to_png(a1), use_container_width=True)
    with ov2:
        _col_label("Drawing 2 — Variant")
        st.image(to_png(a2), use_container_width=True)


def render_identical_aspects(identical: list) -> None:
    if not identical:
        return
    with st.expander("✅  Unchanged aspects", expanded=False):
        pills = " ".join(
            f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;'
            f'color:#34d399;background:rgba(52,211,153,.1);'
            f'border:1px solid rgba(52,211,153,.25);padding:3px 10px;'
            f'border-radius:3px;margin:2px;display:inline-block">{it}</span>'
            for it in identical
        )
        st.markdown(pills, unsafe_allow_html=True)
