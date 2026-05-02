"""
api.py
Handles all communication with the Anthropic Claude API.
"""

import base64
import json

import anthropic

from constants import COMPARE_PROMPT


def _encode_image(data: bytes) -> str:
    return base64.standard_b64encode(data).decode()


def _get_mime(file) -> str:
    return "image/jpeg" if file.type == "image/jpg" else file.type


def run_compare(f1, f2) -> dict:
    """
    Send both drawing files to Claude and return the parsed JSON result.

    Parameters
    ----------
    f1, f2 : UploadedFile
        Streamlit file-uploader objects for Drawing 1 and Drawing 2.

    Returns
    -------
    dict  with keys: summary, differences, identical_aspects, total_differences
    """
    client = anthropic.Anthropic()
    b1, b2 = f1.read(), f2.read()

    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text",  "text": "Drawing 1:"},
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": _get_mime(f1),
                    "data": _encode_image(b1),
                }},
                {"type": "text",  "text": "Drawing 2:"},
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": _get_mime(f2),
                    "data": _encode_image(b2),
                }},
                {"type": "text",  "text": COMPARE_PROMPT},
            ],
        }],
    )

    raw = resp.content[0].text.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
