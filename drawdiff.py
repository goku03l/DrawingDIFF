"""
app.py
Entry point for DrawingDiff.

Run with:  streamlit run app.py

Module layout
─────────────
app.py            ← entry point (page config + orchestration only)
constants.py      ← SEV_COLORS, COMPARE_PROMPT, conf_color()
styles.py         ← get_css()
api.py            ← run_compare()
image_utils.py    ← pct_to_px, annotate_image, crop_diff, add_border, to_png
ui/
  header.py       ← render_header()
  upload.py       ← render_upload()
  overview.py     ← render_metrics(), render_summary_card(),
                     render_annotated_overview(), render_identical_aspects()
  gallery.py      ← render_gallery()
  inspect.py      ← render_inspect_panel()
"""

import io
import sys
import os

# Streamlit Cloud runs the script from a different cwd than the file's location.
# This ensures all sibling modules (ui/, api.py, etc.) are always importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure the directory containing this file is always on sys.path so that
# sibling modules (api, constants, styles, ui/) resolve correctly regardless
# of the working directory Streamlit Cloud uses.
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
from ui.gallery import render_gallery
from ui.inspect import render_inspect_panel

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DrawingDiff — Engineering Comparator",
    page_icon="ui/icon.png",
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
    with st.spinner("Analyzing…"):
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

    render_metrics(diffs, total)
    render_summary_card(result.get("summary", ""))
    render_annotated_overview(img1, img2, diffs, sel_id)
    render_identical_aspects(result.get("identical_aspects", []))

    st.markdown("---")

    if not diffs:
        st.info("No differences detected — the drawings appear identical.")
    else:
        tbl_col, ins_col = st.columns([5, 4], gap="large")
        with tbl_col:
            render_gallery(diffs, sel_id)
        with ins_col:
            render_inspect_panel(sel_diff, img1, img2)
