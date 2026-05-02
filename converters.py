"""
converters.py
Normalises any supported file format into a PIL Image (RGB/RGBA).

Supported inputs
----------------
Raster  : PNG, JPG/JPEG, WEBP, TIFF/TIF  (handled by Pillow)
Vector  : SVG                             (rasterised via cairosvg)
Document: PDF                             (first page via pdf2image / poppler)

All converters return a PIL Image ready for annotation and base64 encoding.
"""

import io
from PIL import Image


# ── Raster (Pillow handles these directly) ────────────────────────────────────

def _from_raster(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    img.load()                        # force decode (needed for TIFF)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    return img


# ── SVG → PNG via cairosvg ────────────────────────────────────────────────────

def _from_svg(data: bytes, dpi: int = 150) -> Image.Image:
    try:
        import cairosvg
    except ImportError:
        raise ImportError(
            "cairosvg is required for SVG support. "
            "Add 'cairosvg' to requirements.txt and redeploy."
        )
    png_bytes = cairosvg.svg2png(bytestring=data, dpi=dpi)
    return _from_raster(png_bytes)


# ── PDF → PNG via pdf2image (needs poppler) ───────────────────────────────────

def _from_pdf(data: bytes, dpi: int = 150) -> Image.Image:
    try:
        from pdf2image import convert_from_bytes
    except ImportError:
        raise ImportError(
            "pdf2image is required for PDF support. "
            "Add 'pdf2image' to requirements.txt and redeploy."
        )
    pages = convert_from_bytes(data, dpi=dpi, first_page=1, last_page=1)
    if not pages:
        raise ValueError("Could not render any page from the PDF.")
    img = pages[0]
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    return img


# ── Public API ────────────────────────────────────────────────────────────────

#: All file extensions accepted by the upload widget
ACCEPTED_TYPES = ["png", "jpg", "jpeg", "webp", "tif", "tiff", "svg", "pdf"]

#: Map lowercase extension → converter function
_CONVERTERS = {
    "png":  _from_raster,
    "jpg":  _from_raster,
    "jpeg": _from_raster,
    "webp": _from_raster,
    "tif":  _from_raster,
    "tiff": _from_raster,
    "svg":  _from_svg,
    "pdf":  _from_pdf,
}


def to_pil(file) -> Image.Image:
    """
    Convert a Streamlit UploadedFile of any supported type to a PIL Image.

    Parameters
    ----------
    file : streamlit.runtime.uploaded_file_manager.UploadedFile

    Returns
    -------
    PIL.Image.Image  in RGB or RGBA mode
    """
    ext = file.name.rsplit(".", 1)[-1].lower()
    converter = _CONVERTERS.get(ext)
    if converter is None:
        raise ValueError(f"Unsupported file type: .{ext}")
    data = file.read()
    file.seek(0)          # reset so callers can re-read if needed
    return converter(data)


def to_png_bytes(file) -> bytes:
    """
    Convert any supported file to raw PNG bytes (for Claude API / PIL ops).
    Resets the file cursor afterwards.
    """
    img = to_pil(file)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    file.seek(0)
    return buf.getvalue()
