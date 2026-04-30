import os
import base64
import json
import streamlit as st
import anthropic

st.set_page_config(
    page_title="DrawingDiff — Engineering Comparator",
    page_icon="⬡",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap');

[data-testid="stAppViewContainer"] { background: #0e0f11; }
[data-testid="stHeader"] { background: #16181c; border-bottom: 1px solid #2a2d34; }
section[data-testid="stSidebar"] { background: #16181c; border-right: 1px solid #2a2d34; }

h1, h2, h3, p, label, div { color: #e8eaf0 !important; }

[data-testid="metric-container"] {
    background: #16181c !important;
    border: 1px solid #2a2d34 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] label {
    color: #6b7280 !important;
    font-size: 11px !important;
    letter-spacing: .06em;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 22px !important;
}

[data-testid="stFileUploader"] {
    background: #16181c !important;
    border: 1.5px dashed #383c46 !important;
    border-radius: 8px !important;
    padding: .5rem !important;
}

.stButton > button {
    background: #00d4aa !important;
    color: #0e0f11 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important;
    border: none !important;
    border-radius: 5px !important;
    padding: .55rem 1.6rem !important;
    letter-spacing: .06em !important;
}
.stButton > button:hover { opacity: .88 !important; }
</style>
""", unsafe_allow_html=True)

COMPARE_PROMPT = """You are an expert mechanical/engineering drawing analyst.
Two 2D engineering drawings are provided — they depict the same part or assembly.

Carefully compare them and identify ALL differences between Drawing 1 and Drawing 2.

Focus on:
- Dimensions and measurements (lengths, widths, heights, radii, angles, tolerances)
- Geometric features (holes, slots, chamfers, fillets, threads, grooves)
- Annotations and labels (text, part numbers, revision marks, title block)
- Line types and symbols (hidden lines, center lines, section cuts, surface finish)
- Views present (top, front, side, isometric, section views)
- GD&T symbols and datums
- Material callouts or notes
- Any added, removed, or modified features

Respond ONLY with a valid JSON object — no markdown fences, no extra text:
{
  "summary": "One-sentence summary of the overall differences",
  "differences": [
    {
      "id": 1,
      "category": "Category (e.g. Dimensions, Features, Annotations, GD&T, Notes)",
      "element": "Specific element being compared",
      "drawing1": "What Drawing 1 shows",
      "drawing2": "What Drawing 2 shows",
      "severity": "minor|moderate|major"
    }
  ],
  "identical_aspects": ["aspects that appear unchanged"],
  "total_differences": <number>
}

If drawings are identical, return an empty differences array with total_differences: 0."""


def encode_image(data: bytes) -> str:
    return base64.standard_b64encode(data).decode()


def get_mime(file) -> str:
    t = file.type
    return "image/jpeg" if t == "image/jpg" else t


def run_compare(f1, f2) -> dict:

    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    b1, b2 = f1.read(), f2.read()

    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Drawing 1:"},
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": get_mime(f1),
                    "data": encode_image(b1),
                }},
                {"type": "text", "text": "Drawing 2:"},
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": get_mime(f2),
                    "data": encode_image(b2),
                }},
                {"type": "text", "text": COMPARE_PROMPT},
            ],
        }],
    )

    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;padding:.25rem 0 1.5rem">
  <div style="width:32px;height:32px;background:#00d4aa;border-radius:5px;
              display:grid;place-items:center;font-size:18px;flex-shrink:0">⬡</div>
  <span style="font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:500">
    Drawing<span style="color:#00d4aa">Diff</span>
  </span>
  <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#6b7280 !important;
               background:#16181c;border:1px solid #2a2d34;padding:3px 10px;
               border-radius:3px;letter-spacing:.05em;margin-left:auto">
    Engineering Drawing Comparator
  </span>
</div>
""", unsafe_allow_html=True)

# ─── Upload ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                'letter-spacing:.06em;text-transform:uppercase;color:#6b7280 !important;'
                'margin-bottom:4px">Drawing 1 — Reference</p>', unsafe_allow_html=True)
    f1 = st.file_uploader("Drawing 1", type=["png", "jpg", "jpeg", "webp"],
                           label_visibility="collapsed", key="f1")
    if f1:
        st.image(f1, use_container_width=True)

with col2:
    st.markdown('<p style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                'letter-spacing:.06em;text-transform:uppercase;color:#6b7280 !important;'
                'margin-bottom:4px">Drawing 2 — Variant</p>', unsafe_allow_html=True)
    f2 = st.file_uploader("Drawing 2", type=["png", "jpg", "jpeg", "webp"],
                           label_visibility="collapsed", key="f2")
    if f2:
        st.image(f2, use_container_width=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ─── Compare button ───────────────────────────────────────────────────────────
btn_col, _ = st.columns([1, 5])
with btn_col:
    clicked = st.button("⬡  COMPARE DRAWINGS", disabled=not (f1 and f2))

# ─── Results ──────────────────────────────────────────────────────────────────
if clicked and f1 and f2:
    with st.spinner("Analyzing with Claude Vision…"):
        try:
            result = run_compare(f1, f2)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    diffs   = result.get("differences", [])
    total   = result.get("total_differences", len(diffs))
    major   = sum(1 for d in diffs if d.get("severity") == "major")
    moderate = sum(1 for d in diffs if d.get("severity") == "moderate")
    minor   = sum(1 for d in diffs if d.get("severity") == "minor")

    st.markdown("---")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Differences", total)
    m2.metric("🔴 Major", major)
    m3.metric("🟡 Moderate", moderate)
    m4.metric("🔵 Minor", minor)

    # Summary
    if result.get("summary"):
        st.markdown(
            f'<div style="background:#16181c;border:1px solid #2a2d34;border-radius:8px;'
            f'padding:1rem 1.25rem;margin:.75rem 0 1.25rem;color:#9ca3af !important;'
            f'font-size:13px;line-height:1.7">{result["summary"]}</div>',
            unsafe_allow_html=True,
        )

    # Identical aspects
    identical = result.get("identical_aspects", [])
    if identical:
        with st.expander("✅  Unchanged aspects", expanded=False):
            pills = " ".join(
                f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;'
                f'color:#34d399;background:rgba(52,211,153,.1);'
                f'border:1px solid rgba(52,211,153,.25);padding:3px 10px;'
                f'border-radius:3px;margin:2px;display:inline-block">{item}</span>'
                for item in identical
            )
            st.markdown(pills, unsafe_allow_html=True)

    # Difference table
    st.markdown("### Difference Table")

    if not diffs:
        st.info("No differences detected — the drawings appear identical.")
    else:
        SEV = {"major": "🔴 MAJOR", "moderate": "🟡 MODERATE", "minor": "🔵 MINOR"}
        rows = [
            {
                "#": d.get("id", i + 1),
                "Severity": SEV.get(d.get("severity", "minor"), d.get("severity", "")),
                "Category": d.get("category", ""),
                "Element": d.get("element", ""),
                "Drawing 1": d.get("drawing1", ""),
                "Drawing 2": d.get("drawing2", ""),
            }
            for i, d in enumerate(diffs)
        ]

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
            column_config={
                "#":         st.column_config.NumberColumn(width="small"),
                "Severity":  st.column_config.TextColumn(width="small"),
                "Category":  st.column_config.TextColumn(width="medium"),
                "Element":   st.column_config.TextColumn(width="medium"),
                "Drawing 1": st.column_config.TextColumn(width="large"),
                "Drawing 2": st.column_config.TextColumn(width="large"),
            },
        )
