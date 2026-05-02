"""
ui/header.py
Renders the application header bar.
"""

import streamlit as st


def render_header() -> None:
    st.markdown("""
<div style="display:flex;align-items:center;gap:12px;padding:.25rem 0 1.5rem">
  <div style="width:32px;height:32px;background:#00d4aa;border-radius:5px;
              display:grid;place-items:center;font-size:18px">⬡</div>
  <span style="font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:500">
    Drawing<span style="color:#00d4aa">Diff</span>
  </span>
  <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;
               color:#6b7280 !important;background:#16181c;border:1px solid #2a2d34;
               padding:3px 10px;border-radius:3px;letter-spacing:.05em;margin-left:auto">
    Engineering Drawing Comparator
  </span>
</div>
""", unsafe_allow_html=True)
