import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from PIL import Image

from styles  import get_css
from api     import run_compare
from ui.header   import render_header
from ui.upload   import render_upload
from ui.overview import (
    render_metrics,
    render_summary_card,
    render_annotated_overview,
    render_identical_aspects,
)
from ui.table   import render_table
from ui.inspect import render_inspect_panel

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DrawingDiff — Engineering Comparator",
    page_icon="ui\icon.png",   # or "icon.svg"
    layout="wide",
)
st.markdown(get_css(), unsafe_allow_html=True)

# ── Session-state defaults ────────────────────────────────────────────────────
for key, default in [
    ("result",  None),
    ("img1b",   None),
    ("img2b",   None),
    ("sel_id",  None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Header + upload ───────────────────────────────────────────────────────────
render_header()
f1, f2 = render_upload()

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

bcol, _ = st.columns([1, 5])
with bcol:
    clicked = st.button("⬡  COMPARE DRAWINGS", disabled=not (f1 and f2))

# ── Run comparison ────────────────────────────────────────────────────────────
if clicked and f1 and f2:
    with st.spinner("Analyzing with Claude Vision…"):
        try:
            st.session_state.result = run_compare(f1, f2)
            f1.seek(0)
            f2.seek(0)
            st.session_state.img1b  = f1.read()
            st.session_state.img2b  = f2.read()
            st.session_state.sel_id = None
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

# ── Render results ────────────────────────────────────────────────────────────
if st.session_state.result:
    result   = st.session_state.result
    img1     = Image.open(io.BytesIO(st.session_state.img1b))
    img2     = Image.open(io.BytesIO(st.session_state.img2b))
    diffs    = result.get("differences", [])
    total    = result.get("total_differences", len(diffs))
    sel_id   = st.session_state.sel_id
    sel_diff = next((d for d in diffs if d.get("id") == sel_id), None)

    st.markdown("---")

    # Summary strip
    render_metrics(diffs, total)
    render_summary_card(result.get("summary", ""))

    # Annotated drawing overview (full images with bbox overlays)
    render_annotated_overview(img1, img2, diffs, sel_id)

    # Unchanged aspects pill strip
    render_identical_aspects(result.get("identical_aspects", []))

    st.markdown("---")

    if not diffs:
        st.info("No differences detected — the drawings appear identical.")
    else:
        # ── Split layout: table LEFT | inspect RIGHT ──────────────────────────
        tbl_col, ins_col = st.columns([5, 4], gap="large")

        with tbl_col:
            render_table(diffs, sel_id)

        with ins_col:
            render_inspect_panel(sel_diff, img1, img2)
