"""
ui/inspect.py
Renders the right-hand inspect panel for a selected difference.
Shows: title card, confidence bar, description cards, cropped images.
"""

import streamlit as st
from PIL import Image

from constants import SEV_COLORS, conf_color
from image_utils import crop_diff, add_border, to_png


def render_inspect_panel(
    sel_diff: dict | None,
    img1: Image.Image,
    img2: Image.Image,
) -> None:
    """
    Render the inspect panel.

    Parameters
    ----------
    sel_diff : dict | None   — the currently selected difference, or None
    img1, img2               — PIL images for Drawing 1 and Drawing 2
    """
    st.markdown("### Inspect")

    if sel_diff is None:
        _render_empty_state()
        return

    d     = sel_diff
    sev   = d.get("severity", "minor")
    chex  = SEV_COLORS.get(sev, SEV_COLORS["minor"])["hex"]
    rgb   = SEV_COLORS.get(sev, SEV_COLORS["minor"])["rgb"]
    lbl   = SEV_COLORS.get(sev, SEV_COLORS["minor"])["label"]
    conf  = int(d.get("confidence", 70))
    cc    = conf_color(conf)
    bd1   = d.get("bbox_d1")
    bd2   = d.get("bbox_d2")

    _render_title_card(d, chex, lbl)
    _render_confidence_bar(conf, cc)
    _render_description_cards(d, chex)
    _render_crops(d, img1, img2, bd1, bd2, rgb)


# ── Private helpers ───────────────────────────────────────────────────────────

def _render_empty_state() -> None:
    st.markdown(
        '<div style="background:#16181c;border:1px dashed #2a2d34;'
        'border-radius:8px;padding:3rem 1.5rem;text-align:center;'
        'color:#4b5563 !important;font-family:\'IBM Plex Mono\',monospace;'
        'font-size:12px;margin-top:.5rem;line-height:2">'
        '← Click 🔍 on any row<br>to inspect that difference'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_title_card(d: dict, chex: str, lbl: str) -> None:
    st.markdown(
        f'<div style="background:#16181c;border:1px solid {chex}44;'
        f'border-radius:8px;padding:.8rem 1rem;margin-bottom:.75rem">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:#6b7280 !important;text-transform:uppercase;letter-spacing:.07em;'
        f'margin-bottom:3px">#{d["id"]} · {d.get("category", "")} · '
        f'<span style="color:{chex}">{lbl}</span></div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:13px;'
        f'color:#e8eaf0 !important;font-weight:500">{d.get("element", "")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_confidence_bar(conf: int, cc: str) -> None:
    st.markdown(
        f'<div style="margin-bottom:.9rem">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:#6b7280 !important;text-transform:uppercase;letter-spacing:.07em;'
        f'margin-bottom:4px">Confidence — <span style="color:{cc}">{conf}%</span></div>'
        f'<div class="conf-track">'
        f'<div class="conf-fill" style="width:{conf}%;background:{cc}"></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _render_description_cards(d: dict, chex: str) -> None:
    dc1, dc2 = st.columns(2)
    for col, label_txt, txt_key in [
        (dc1, "Drawing 1", "drawing1"),
        (dc2, "Drawing 2", "drawing2"),
    ]:
        with col:
            st.markdown(
                f'<div style="background:#0e0f11;border-left:3px solid {chex};'
                f'border-radius:4px;padding:.6rem .8rem;font-size:10px;'
                f'font-family:\'IBM Plex Mono\',monospace;margin-bottom:.6rem">'
                f'<div style="color:#6b7280 !important;font-size:8px;'
                f'text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px">'
                f'{label_txt}</div>'
                f'<div style="color:#d1d5db !important">{d.get(txt_key, "—")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_crops(
    d: dict,
    img1: Image.Image,
    img2: Image.Image,
    bd1: dict | None,
    bd2: dict | None,
    rgb: tuple,
) -> None:
    ic1, ic2 = st.columns(2)
    for col, img_src, bbox, cap in [
        (ic1, img1, bd1, "Drawing 1"),
        (ic2, img2, bd2, "Drawing 2"),
    ]:
        with col:
            if bbox:
                crop = crop_diff(img_src, bbox, ctx=0.03)
                crop = add_border(crop, rgb)
                st.image(
                    to_png(crop),
                    use_container_width=True,
                    caption=f"{cap} · region #{d['id']}",
                )
            else:
                st.caption(f"No location data for {cap}")
