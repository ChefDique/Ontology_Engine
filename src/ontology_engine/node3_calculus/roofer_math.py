"""
Roofer Math — TASK_B3

Industry-specific mathematical conversions for roofing materials.
ALL math is deterministic Python — LLMs never touch this.

Source: DOC_004 Lexicon Matrix + Conversion Formulas

Design by Contract:
  Invariant: No floating-point rounding errors in currency.
             Bundle counts ALWAYS round UP (math.ceil).
"""

import math

from ..node2_extraction.lexicon_matrix import lookup_code


def squares_to_bundles(squares: float, waste_factor: float = 1.0) -> int:
    """Convert roofing squares to bundles.

    Standard: 1 square = 3 bundles.
    Waste factor: 1.0 = no waste, 1.15 = 15% steep-pitch waste.

    ALWAYS rounds UP — never round down on physical materials.
    """
    raw = squares * 3 * waste_factor
    return math.ceil(raw)


def linear_feet_to_pieces(linear_feet: float, piece_length: float = 10.0) -> int:
    """Convert linear feet to piece count.

    Standard starter/ridge pieces are 10 ft.
    ALWAYS rounds UP.
    """
    return math.ceil(linear_feet / piece_length)


def apply_pitch_waste(quantity: float, pitch_category: str) -> float:
    """Apply waste factor based on roof pitch category.

    Pitch categories and their waste factors:
      - 'low'    (0-6/12):  5%  → 1.05
      - 'medium' (7-9/12):  10% → 1.10
      - 'steep'  (10+/12):  15% → 1.15
    """
    waste_factors = {
        "low": 1.05,
        "medium": 1.10,
        "steep": 1.15,
    }
    factor = waste_factors.get(pitch_category, 1.0)
    return quantity * factor


def square_feet_to_sheets(square_feet: float, sheet_size: float = 32.0) -> int:
    """Convert square feet to sheet count (drywall, siding panels).

    Standard 4x8 sheet = 32 SF.
    ALWAYS rounds UP.
    """
    return math.ceil(square_feet / sheet_size)


# ─── Conversion dispatch table ──────────────────────────────────────────────
# Maps (category_code, unit_of_measure) to a converter function.
# Each converter: (quantity, pitch_category) → (physical_qty, physical_unit)

_CONVERTERS: dict[tuple[str, str], callable] = {
    ("RFG", "SQ"): lambda qty, pitch: (
        squares_to_bundles(qty, waste_factor=_pitch_to_waste(pitch)),
        "bundles",
    ),
    ("GUT", "LF"): lambda qty, pitch: (
        linear_feet_to_pieces(qty),
        "pieces",
    ),
    ("SID", "SF"): lambda qty, pitch: (
        square_feet_to_sheets(qty),
        "sheets",
    ),
    ("DRY", "SF"): lambda qty, pitch: (
        square_feet_to_sheets(qty),
        "sheets",
    ),
}


def _pitch_to_waste(pitch_category: str) -> float:
    """Get multiplicative waste factor for a pitch category."""
    return {"low": 1.05, "medium": 1.10, "steep": 1.15}.get(pitch_category, 1.0)


def calculate_material_quantities(
    line_items: list[dict], pitch_category: str = "low"
) -> list[dict]:
    """Convert all line items from Xactimate units to physical material quantities.

    For each line item:
    1. Look up the category in the Lexicon Matrix for trade info.
    2. Apply the appropriate unit converter if one exists.
    3. Fall back to raw quantity with original UOM if no converter.
    4. Apply pitch waste for roofing items.

    Returns: list of dicts with added 'physical_qty', 'physical_unit', and 'trade'.
    """
    results = []

    for item in line_items:
        category = item.get("category", "")
        uom = item.get("unit_of_measure", "")
        quantity = item.get("quantity", 0)
        description = item.get("description", "")

        # Look up trade from lexicon
        lexicon_entry = lookup_code(category)
        trade = lexicon_entry["trade"] if lexicon_entry else "general"

        # Try dispatching to a specialized converter
        converter_key = (category.upper(), uom.upper())
        converter = _CONVERTERS.get(converter_key)

        if converter:
            physical_qty, physical_unit = converter(quantity, pitch_category)
        else:
            # No special conversion — use quantity as-is with ceil
            physical_qty = math.ceil(quantity) if quantity > 0 else 0
            physical_unit = uom.lower() if uom else "units"

        result = {
            "category": category,
            "description": description,
            "physical_qty": physical_qty,
            "physical_unit": physical_unit,
            "trade": trade,
        }

        # Carry forward unit_cost if present
        if "unit_price" in item:
            result["unit_cost"] = item["unit_price"]

        results.append(result)

    return results
