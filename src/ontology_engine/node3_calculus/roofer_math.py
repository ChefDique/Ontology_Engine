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


def calculate_material_quantities(line_items: list[dict], pitch_category: str = "low") -> list[dict]:
    """Convert all line items from Xactimate units to physical material quantities.

    Returns: list of line items with added 'physical_qty' and 'physical_unit' fields.
    """
    raise NotImplementedError("TASK_B3: Full material quantity calculation")
