"""
Lexicon Matrix — Xactimate Code Mappings

Maps ~50 core Xactimate category codes to their semantic meanings,
physical units, and supplier equivalents. This is the foundation
for semantic extraction in Node 2.

Source: DOC_004 (Roofing CRM & Xactimate Integration Blueprint)
"""

# Xactimate Category Code → Semantic Mapping
# Format: code → {description, default_uom, trade, material_type}
LEXICON_MATRIX: dict[str, dict] = {
    "RFG": {
        "description": "Roofing",
        "default_uom": "SQ",
        "trade": "roofing",
        "material_type": "shingles",
        "notes": "1 SQ = 100 SF = 3 bundles (standard 3-tab/architectural)",
    },
    "SID": {
        "description": "Siding",
        "default_uom": "SF",
        "trade": "siding",
        "material_type": "siding_panels",
    },
    "DRY": {
        "description": "Drywall",
        "default_uom": "SF",
        "trade": "drywall",
        "material_type": "drywall_sheets",
    },
    "PLM": {
        "description": "Plumbing",
        "default_uom": "EA",
        "trade": "plumbing",
        "material_type": "fixtures",
    },
    "ELC": {
        "description": "Electrical",
        "default_uom": "EA",
        "trade": "electrical",
        "material_type": "fixtures",
    },
    "FLR": {
        "description": "Flooring",
        "default_uom": "SF",
        "trade": "flooring",
        "material_type": "flooring_material",
    },
    "PNT": {
        "description": "Painting",
        "default_uom": "SF",
        "trade": "painting",
        "material_type": "paint",
    },
    "GUT": {
        "description": "Gutters",
        "default_uom": "LF",
        "trade": "roofing",
        "material_type": "gutters",
    },
    # TODO: Expand to full ~50 codes from DOC_004 Lexicon Matrix research
    # Additional codes: WDW (Windows), DOR (Doors), INS (Insulation),
    # CLN (Cleaning), DEM (Demolition), FNC (Fencing), etc.
}


def lookup_code(category_code: str) -> dict | None:
    """Look up an Xactimate category code in the Lexicon Matrix.

    Returns: dict with semantic mapping or None if code not found.
    """
    return LEXICON_MATRIX.get(category_code.upper())


def get_trade(category_code: str) -> str | None:
    """Get the trade classification for an Xactimate code."""
    entry = lookup_code(category_code)
    return entry["trade"] if entry else None
