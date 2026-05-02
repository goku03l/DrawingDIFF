import io
import sys
import os

# Must be FIRST before any local imports.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from PIL import Image

from styles     import get_css
from api        import run_compare
from converters import to_pil
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

st.set_page_config(
    page_title="DrawingDiff — Engineering Comparator",
    page_icon="⬡",
    layout="wide",
)
st.markdown(get_css(), unsafe_allow_html=True)

for key, default in [
    ("result",  None),
    ("img1b",   None),
    ("img2b",   None),
    ("sel_id",  None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

render_header()
f1, f2 = render_upload()

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

bcol, _ = st.columns([1, 5])
with bcol:
    clicked = st.button("⬡  COMPARE DRAWINGS", disabled=not (f1 and f2))

if clicked and f1 and f2:
    with st.spinner("Analyzing with Claude Vision…"):
        try:
            st.session_state.result = run_compare(f1, f2)
            # Convert to PIL → PNG bytes so all formats are stored uniformly
            def _to_png_bytes(file):
                img = to_pil(file)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return buf.getvalue()
            st.session_state.img1b  = _to_png_bytes(f1)
            st.session_state.img2b  = _to_png_bytes(f2)
            st.session_state.sel_id = None
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

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
