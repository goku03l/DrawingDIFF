"""
image_utils.py
PIL-based image utilities: coordinate conversion, annotation drawing,
region cropping, and serialisation helpers.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import io

from PIL import Image, ImageDraw, ImageFont

from constants import SEV_COLORS

# Path to a bundled bold font; falls back to PIL's built-in default.
_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_BADGE_FONT_SIZE = 13


def _load_font(size: int = _BADGE_FONT_SIZE) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(_FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


# ── Coordinate helpers ────────────────────────────────────────────────────────

def pct_to_px(bbox: dict, W: int, H: int) -> tuple[int, int, int, int]:
    """
    Convert a percentage-based bounding box to pixel coordinates.

    Handles:
    - Missing / non-numeric keys (defaults to 0)
    - Out-of-bounds values (clamped to image dimensions)
    - Inverted coordinates  (x1 > x2 or y1 > y2 — swapped automatically)
    - Degenerate boxes      (enforces a 4 px minimum side length)

    Parameters
    ----------
    bbox : dict  with keys x, y, w, h  (all as % of image dimension)
    W, H : int   image width and height in pixels

    Returns
    -------
    (x1, y1, x2, y2) in pixels, guaranteed valid for PIL draw calls
    """
    ax = max(0.0, float(bbox.get("x", 0)))
    ay = max(0.0, float(bbox.get("y", 0)))
    aw = max(0.0, float(bbox.get("w", 0)))
    ah = max(0.0, float(bbox.get("h", 0)))

    x1 = int(ax        / 100 * W)
    y1 = int(ay        / 100 * H)
    x2 = int((ax + aw) / 100 * W)
    y2 = int((ay + ah) / 100 * H)

    # Clamp to image bounds
    x1, x2 = max(0, min(x1, W - 1)), max(0, min(x2, W - 1))
    y1, y2 = max(0, min(y1, H - 1)), max(0, min(y2, H - 1))

    # Normalise direction
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # Enforce minimum size
    if x2 - x1 < 4:
        x2 = min(W - 1, x1 + 4)
    if y2 - y1 < 4:
        y2 = min(H - 1, y1 + 4)

    return x1, y1, x2, y2


# ── Drawing ───────────────────────────────────────────────────────────────────

def annotate_image(
    img: Image.Image,
    diffs: list,
    key: str,
    selected_id: int | None = None,
) -> Image.Image:
    """
    Return a copy of *img* with numbered, colour-coded bounding boxes drawn
    for every difference in *diffs* that has a bbox for *key* ("d1" or "d2").

    The box for *selected_id* is rendered brighter and with a thicker border.
    """
    out     = img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    W, H    = img.size
    fnt     = _load_font()

    for d in diffs:
        bbox = d.get(f"bbox_{key}")
        if not bbox:
            continue

        sev    = d.get("severity", "minor")
        rgb    = SEV_COLORS.get(sev, SEV_COLORS["minor"])["rgb"]
        did    = d.get("id", 0)
        is_sel = (did == selected_id)

        x1, y1, x2, y2 = pct_to_px(bbox, W, H)

        # Fill + border
        draw.rectangle([x1, y1, x2, y2], fill=(*rgb, 55 if is_sel else 20))
        lw = 3 if is_sel else 2
        for t in range(lw):
            draw.rectangle(
                [x1 - t, y1 - t, x2 + t, y2 + t],
                outline=(*rgb, 255 if is_sel else 180),
            )

        # Numeric badge above (or below) the box
        bs = 18
        bx = x1
        by = y1 - bs if y1 >= bs else y2
        draw.rectangle([bx, by, bx + bs, by + bs], fill=(*rgb, 230))
        draw.text((bx + 3, by + 2), str(did), fill=(255, 255, 255, 255), font=fnt)

    return Image.alpha_composite(out, overlay).convert("RGB")


def crop_diff(
    img: Image.Image,
    bbox: dict,
    ctx: float = 0.03,
) -> Image.Image:
    """
    Crop the region described by *bbox* from *img*, adding a small
    context border of *ctx* × image-dimension pixels on each side.
    """
    W, H = img.size
    x1, y1, x2, y2 = pct_to_px(bbox, W, H)
    px, py = int(W * ctx), int(H * ctx)
    return img.crop((
        max(0, x1 - px),
        max(0, y1 - py),
        min(W, x2 + px),
        min(H, y2 + py),
    ))


def add_border(img: Image.Image, rgb: tuple) -> Image.Image:
    """Draw a 3-pixel coloured border around *img* in-place and return it."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    for t in range(3):
        draw.rectangle([t, t, W - 1 - t, H - 1 - t], outline=(*rgb, 230))
    return img


# ── Serialisation ─────────────────────────────────────────────────────────────

def to_png(img: Image.Image) -> bytes:
    """Serialise a PIL image to PNG bytes."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
