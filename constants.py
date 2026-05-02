"""
constants.py
Shared configuration: severity colour map, confidence helper, and the
Claude comparison prompt.
"""

SEV_COLORS: dict[str, dict] = {
    "major":    {"rgb": (239,  68,  68), "hex": "#ef4444", "label": "🔴 MAJOR"},
    "moderate": {"rgb": (234, 179,   8), "hex": "#eab308", "label": "🟡 MODERATE"},
    "minor":    {"rgb": ( 59, 130, 246), "hex": "#3b82f6", "label": "🔵 MINOR"},
}


def conf_color(score: int) -> str:
    """Return a hex colour for a confidence score (0-100)."""
    if score >= 80:
        return "#00d4aa"
    if score >= 55:
        return "#eab308"
    return "#ef4444"


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

BOUNDING BOX INSTRUCTIONS — BE PRECISE:
For every difference provide bbox_d1 and bbox_d2 — the TIGHT rectangular region in each
image where that change is visible.
  x = left edge of changed element as % of image WIDTH   (0=far left,   100=far right)
  y = top  edge of changed element as % of image HEIGHT  (0=very top,   100=very bottom)
  w = width  of changed element as % of image WIDTH
  h = height of changed element as % of image HEIGHT
Rules:
  - Boxes must be TIGHT around the element — do NOT add extra whitespace.
  - Small annotations: typical w=5-15, h=3-8.
  - Larger features: scale accordingly but stay tight.
  - Example: a small dimension label near top-right → x:72, y:6, w:12, h:5

CONFIDENCE SCORE — for each difference rate 0-100:
  100 = you can clearly see and read the difference
  70  = visible but slightly ambiguous
  40  = inferred from context, not clearly legible
  0   = pure guess

Respond ONLY with valid JSON — no markdown fences, no extra text:
{
  "summary": "One-sentence overall summary",
  "differences": [
    {
      "id": 1,
      "category": "Dimensions|Features|Annotations|GD&T|Notes|Line Types|Views",
      "element": "Specific element name",
      "drawing1": "What Drawing 1 shows",
      "drawing2": "What Drawing 2 shows",
      "severity": "minor|moderate|major",
      "confidence": 85,
      "bbox_d1": {"x": 12.5, "y": 34.0, "w": 8.0, "h": 5.0},
      "bbox_d2": {"x": 12.5, "y": 34.0, "w": 8.0, "h": 5.0}
    }
  ],
  "identical_aspects": ["unchanged aspect 1", "..."],
  "total_differences": 3
}
If identical: differences:[], total_differences:0."""
