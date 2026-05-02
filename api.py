"""
api.py
Handles all communication with the Anthropic Claude API.
All file formats are normalised to PNG before encoding.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import base64
import json
import io

import anthropic

from constants  import COMPARE_PROMPT
from converters import to_pil


def _to_png_b64(file) -> str:
    """Convert any supported file type to a base64-encoded PNG string."""
    img = to_pil(file)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()


def run_compare(f1, f2) -> dict:
    """
    Send both drawing files to Claude and return the parsed JSON result.
    Accepts PNG, JPG, WEBP, TIFF, SVG, PDF — all normalised to PNG internally.
    """
    client = anthropic.Anthropic()

    b64_1 = _to_png_b64(f1)
    b64_2 = _to_png_b64(f2)

    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text",  "text": "Drawing 1:"},
                {"type": "image", "source": {
                    "type":       "base64",
                    "media_type": "image/png",   # always PNG after conversion
                    "data":       b64_1,
                }},
                {"type": "text",  "text": "Drawing 2:"},
                {"type": "image", "source": {
                    "type":       "base64",
                    "media_type": "image/png",
                    "data":       b64_2,
                }},
                {"type": "text",  "text": COMPARE_PROMPT},
            ],
        }],
    )

    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
