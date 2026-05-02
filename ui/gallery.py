"""
ui/gallery.py
Replaces ui/table.py with a scrollable card gallery.

Each card shows:
  - Severity badge (colour-coded)
  - ID number
  - Category pill
  - Element name (headline)
  - Confidence bar
  - D1 vs D2 one-liner descriptions
  - Select / Deselect button

Cards are sorted major → moderate → minor.
The gallery sits in a fixed-height scrollable region via st.container + CSS.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import streamlit as st

from constants import SEV_COLORS, conf_color

_SEV_ORDER = {"major": 0, "moderate": 1, "minor": 2}


def _sorted_diffs(diffs: list) -> list:
    return sorted(diffs, key=lambda d: _SEV_ORDER.get(d.get("severity", "minor"), 9))


def render_gallery(diffs: list, sel_id: int | None) -> None:
    """Render the scrollable card gallery and handle selection state."""

    st.markdown("### Differences")
    st.caption(f"{len(diffs)} found · sorted by severity · click a card to inspect")

    # Inject per-gallery CSS once
    st.markdown("""
    <style>
    .dd-card {
        background: #16181c;
        border: 1px solid #2a2d34;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        transition: border-color .15s;
    }
    .dd-card.selected {
        border-color: #00d4aa !important;
        background: #121e1b !important;
    }
    .dd-card:hover { border-color: #3d4350; }

    .dd-sev-badge {
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px; font-weight: 500;
        letter-spacing: .07em; text-transform: uppercase;
        padding: 2px 7px; border-radius: 3px;
        margin-right: 6px;
    }
    .dd-id {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px; color: #4b5563 !important;
        display: inline;
    }
    .dd-cat {
        float: right;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px; color: #6b7280 !important;
        background: #1e2026; border: 1px solid #2a2d34;
        padding: 1px 7px; border-radius: 3px;
        text-transform: uppercase; letter-spacing: .05em;
    }
    .dd-element {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px; font-weight: 500;
        color: #e8eaf0 !important;
        margin: 6px 0 4px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .dd-conf-row {
        display: flex; align-items: center; gap: 8px;
        margin-bottom: 8px;
    }
    .dd-conf-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px; color: #4b5563 !important;
        white-space: nowrap;
    }
    .dd-conf-track {
        flex: 1; height: 4px; background: #2a2d34;
        border-radius: 2px; overflow: hidden;
    }
    .dd-conf-fill { height: 100%; border-radius: 2px; }
    .dd-conf-pct {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px; white-space: nowrap;
    }
    .dd-desc-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
    }
    .dd-desc-cell {
        background: #0e0f11; border-radius: 4px;
        padding: 5px 8px; font-size: 10px;
        font-family: 'IBM Plex Mono', monospace;
    }
    .dd-desc-label {
        font-size: 8px; text-transform: uppercase;
        letter-spacing: .07em; margin-bottom: 2px;
        color: #4b5563 !important;
    }
    .dd-desc-text { color: #9ca3af !important; line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)

    sorted_diffs = _sorted_diffs(diffs)

    # Scrollable wrapper — fixed height, overflow-y scroll
    st.markdown(
        '<div style="max-height:68vh;overflow-y:auto;'
        'padding-right:4px;scrollbar-width:thin;'
        'scrollbar-color:#2a2d34 transparent">',
        unsafe_allow_html=True,
    )

    for d in sorted_diffs:
        sev    = d.get("severity", "minor")
        chex   = SEV_COLORS.get(sev, SEV_COLORS["minor"])["hex"]
        rgb_s  = f"rgba({','.join(str(v) for v in SEV_COLORS.get(sev, SEV_COLORS['minor'])['rgb'])},0.15)"
        lbl    = SEV_COLORS.get(sev, SEV_COLORS["minor"])["label"]
        did    = d.get("id", 0)
        conf   = int(d.get("confidence", 70))
        cc     = conf_color(conf)
        is_sel = (sel_id == did)

        card_cls = "dd-card selected" if is_sel else "dd-card"
        left_border = f"border-left:3px solid {chex};" if is_sel else ""

        # Truncate long descriptions for the card preview
        d1_txt = (d.get("drawing1") or "—")[:80]
        d2_txt = (d.get("drawing2") or "—")[:80]

        st.markdown(f"""
        <div class="{card_cls}" style="{left_border}">
          <div style="overflow:hidden;margin-bottom:2px">
            <span class="dd-cat">{d.get("category","")}</span>
            <span class="dd-sev-badge" style="background:{rgb_s};color:{chex}">{lbl}</span>
            <span class="dd-id">#{did}</span>
          </div>
          <div class="dd-element" title="{d.get('element','')}">{d.get("element","")}</div>
          <div class="dd-conf-row">
            <span class="dd-conf-label">Confidence</span>
            <div class="dd-conf-track">
              <div class="dd-conf-fill" style="width:{conf}%;background:{cc}"></div>
            </div>
            <span class="dd-conf-pct" style="color:{cc}">{conf}%</span>
          </div>
          <div class="dd-desc-grid">
            <div class="dd-desc-cell">
              <div class="dd-desc-label">Drawing 1</div>
              <div class="dd-desc-text">{d1_txt}</div>
            </div>
            <div class="dd-desc-cell">
              <div class="dd-desc-label">Drawing 2</div>
              <div class="dd-desc-text">{d2_txt}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Invisible-ish button — sits just below each card
        btn_lbl = "✕  Deselect" if is_sel else "🔍  Inspect"
        btn_style = (
            "background:#1a2a25 !important;color:#00d4aa !important;"
            "border:1px solid #00d4aa44 !important;width:100%;margin-bottom:4px;"
        ) if is_sel else (
            "background:#1e2026 !important;color:#6b7280 !important;"
            "border:1px solid #2a2d34 !important;width:100%;margin-bottom:4px;"
        )
        st.markdown(f'<style>#btn_wrap_{did} button{{font-size:10px !important;'
                    f'padding:.3rem .6rem !important;{btn_style}}}</style>'
                    f'<div id="btn_wrap_{did}"></div>', unsafe_allow_html=True)

        if st.button(btn_lbl, key=f"gal_{did}"):
            st.session_state.sel_id = None if is_sel else did
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
