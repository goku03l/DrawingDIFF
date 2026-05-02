"""
styles.py
All application CSS returned as a single string.
Inject with:  st.markdown(get_css(), unsafe_allow_html=True)
"""


def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap');

[data-testid="stAppViewContainer"] { background: #0e0f11; }
[data-testid="stHeader"]           { background: #16181c; border-bottom: 1px solid #2a2d34; }
section[data-testid="stSidebar"]   { background: #16181c; border-right:  1px solid #2a2d34; }

h1, h2, h3, p, label, div { color: #e8eaf0 !important; }

[data-testid="metric-container"] {
    background: #16181c !important; border: 1px solid #2a2d34 !important;
    border-radius: 8px !important; padding: 1rem !important;
}
[data-testid="metric-container"] label {
    color: #6b7280 !important; font-size: 11px !important;
    letter-spacing: .06em; text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 22px !important;
}
[data-testid="stFileUploader"] {
    background: #16181c !important; border: 1.5px dashed #383c46 !important;
    border-radius: 8px !important; padding: .5rem !important;
}

.stButton > button {
    background: #00d4aa !important; color: #0e0f11 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important; border: none !important;
    border-radius: 5px !important; padding: .45rem 1rem !important;
    letter-spacing: .06em !important; font-size: 11px !important;
}
.stButton > button:hover { opacity: .88 !important; }

/* Confidence bar */
.conf-track {
    background: #2a2d34; border-radius: 4px;
    height: 6px; overflow: hidden; margin-top: 4px;
}
.conf-fill { height: 100%; border-radius: 4px; }
</style>
"""
