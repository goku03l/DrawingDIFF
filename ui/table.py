"""
ui/table.py
Renders the interactive difference table.
Each row has a 🔍 / ✕ button that sets st.session_state.sel_id.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import streamlit as st

from constants import SEV_COLORS, conf_color


_TABLE_HEADER_HTML = (
    '<div style="display:grid;grid-template-columns:28px 95px 105px 1fr 52px 44px;'
    'gap:0 8px;padding:6px 8px;background:#1e2026;border:1px solid #2a2d34;'
    'border-radius:6px 6px 0 0;font-family:\'IBM Plex Mono\',monospace;'
    'font-size:9px;letter-spacing:.07em;text-transform:uppercase;color:#6b7280 !important">'
    '<span>#</span><span>Severity</span><span>Category</span>'
    '<span>Element</span><span>Conf.</span><span></span>'
    '</div>'
)

_ROW_SEPARATOR = (
    '<hr style="margin:0;border:none;border-top:1px solid #1e2026">'
)


def render_table(diffs: list, sel_id: int | None) -> None:
    """
    Render the full difference table.
    Clicking a row button writes to st.session_state.sel_id and calls st.rerun().
    """
    st.markdown("### Difference Table")
    st.markdown(_TABLE_HEADER_HTML, unsafe_allow_html=True)

    for i, d in enumerate(diffs):
        sev    = d.get("severity", "minor")
        chex   = SEV_COLORS.get(sev, SEV_COLORS["minor"])["hex"]
        lbl    = SEV_COLORS.get(sev, SEV_COLORS["minor"])["label"]
        did    = d.get("id", i + 1)
        conf   = int(d.get("confidence", 70))
        cc     = conf_color(conf)
        is_sel = (sel_id == did)

        row_bg = "#1a2a25" if is_sel else ("transparent" if i % 2 == 0 else "#13151a")
        row_bl = "border-left:3px solid #00d4aa" if is_sel else "border-left:3px solid transparent"
        cell   = f"font-family:IBM Plex Mono,monospace;background:{row_bg};padding:9px 2px;{row_bl}"

        c0, c1, c2, c3, c4, c5 = st.columns([0.33, 1.1, 1.2, 2.4, 0.65, 0.55])

        with c0:
            st.markdown(f'<div style="{cell};font-size:10px;color:#6b7280">{did}</div>',
                        unsafe_allow_html=True)
        with c1:
            st.markdown(f'<div style="{cell};font-size:9px;color:{chex}">{lbl}</div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="{cell};font-size:10px;color:#9ca3af">'
                        f'{d.get("category", "")}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="{cell};font-size:11px;color:#e8eaf0;font-weight:500">'
                        f'{d.get("element", "")}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="{cell};font-size:11px;color:{cc}">{conf}%</div>',
                        unsafe_allow_html=True)
        with c5:
            if st.button("✕" if is_sel else "🔍", key=f"btn_{did}"):
                st.session_state.sel_id = None if is_sel else did
                st.rerun()

        st.markdown(_ROW_SEPARATOR, unsafe_allow_html=True)
