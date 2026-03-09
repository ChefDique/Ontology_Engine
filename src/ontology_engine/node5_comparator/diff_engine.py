"""
Line-Item Diff Engine — TASK_I2

Compares two sets of procurement items (adjuster vs contractor)
to detect three categories of gaps:
  1. Missing items: present in contractor but not adjuster
  2. Quantity deltas: same item, different quantities (>20% threshold)
  3. Pricing deltas: same item, different unit costs

Matching Strategy:
  Primary key: (category, description) exact match
  Fallback: fuzzy description match within same category (≥80% similarity)
"""

import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Items with quantity difference ≥ this threshold are flagged
QUANTITY_DELTA_THRESHOLD_PCT = 20.0

# Minimum similarity ratio for fuzzy description matching
FUZZY_MATCH_THRESHOLD = 0.80


def _normalize_description(desc: str) -> str:
    """Normalize description for comparison (lowercase, strip whitespace)."""
    return " ".join(desc.lower().strip().split())


def _fuzzy_match_score(desc_a: str, desc_b: str) -> float:
    """Calculate similarity ratio between two descriptions."""
    return SequenceMatcher(
        None,
        _normalize_description(desc_a),
        _normalize_description(desc_b),
    ).ratio()


def _build_item_index(items: list[dict]) -> dict:
    """Build lookup index from (category, normalized_description) → item."""
    index: dict[tuple[str, str], dict] = {}
    for item in items:
        key = (
            item.get("category", "").upper(),
            _normalize_description(item.get("description", "")),
        )
        index[key] = item
    return index


def _find_best_match(
    target: dict,
    candidates: dict[tuple[str, str], dict],
    matched_keys: set,
) -> tuple[str, str] | None:
    """Find the best fuzzy match for target in unmatched candidates."""
    target_cat = target.get("category", "").upper()
    target_desc = _normalize_description(target.get("description", ""))

    best_key = None
    best_score = 0.0

    for key, candidate in candidates.items():
        if key in matched_keys:
            continue
        # Same category required for fuzzy matching
        if key[0] != target_cat:
            continue
        score = _fuzzy_match_score(target_desc, key[1])
        if score >= FUZZY_MATCH_THRESHOLD and score > best_score:
            best_score = score
            best_key = key

    return best_key


def diff_line_items(
    adjuster_items: list[dict],
    contractor_items: list[dict],
) -> list[dict]:
    """Compare adjuster and contractor line items to detect gaps.

    Returns a list of gap dicts, each with:
        - gap_type: 'missing_item' | 'quantity_delta' | 'pricing_delta'
        - description, category, trade, and relevant delta values

    Args:
        adjuster_items: procurement_items from adjuster's Node 3 output
        contractor_items: procurement_items from contractor's Node 3 output

    Returns:
        List of gap dictionaries conforming to NODE_5_OUTPUT_SCHEMA.line_item_gaps
    """
    gaps: list[dict] = []
    adjuster_index = _build_item_index(adjuster_items)
    matched_adjuster_keys: set[tuple[str, str]] = set()

    for c_item in contractor_items:
        c_key = (
            c_item.get("category", "").upper(),
            _normalize_description(c_item.get("description", "")),
        )

        # Try exact match first
        a_item = adjuster_index.get(c_key)
        if a_item:
            matched_adjuster_keys.add(c_key)
        else:
            # Try fuzzy match
            fuzzy_key = _find_best_match(c_item, adjuster_index, matched_adjuster_keys)
            if fuzzy_key:
                a_item = adjuster_index[fuzzy_key]
                matched_adjuster_keys.add(fuzzy_key)

        if a_item is None:
            # Missing item: in contractor but not adjuster
            c_total = c_item.get("unit_cost", 0) * c_item.get("physical_qty", 0)
            gaps.append({
                "gap_type": "missing_item",
                "category": c_item.get("category", ""),
                "description": c_item.get("description", ""),
                "contractor_qty": c_item.get("physical_qty"),
                "adjuster_qty": None,
                "quantity_delta": None,
                "quantity_delta_pct": None,
                "contractor_total": round(c_total, 2),
                "adjuster_total": None,
                "pricing_delta": None,
                "trade": c_item.get("trade", "general"),
            })
            logger.info(
                "Missing item: %s — %s ($%.2f)",
                c_item.get("category", ""),
                c_item.get("description", ""),
                c_total,
            )
        else:
            # Item exists in both — check for quantity and pricing deltas
            c_qty = c_item.get("physical_qty", 0)
            a_qty = a_item.get("physical_qty", 0)
            c_cost = c_item.get("unit_cost", 0)
            a_cost = a_item.get("unit_cost", 0)
            c_total = c_cost * c_qty
            a_total = a_cost * a_qty

            # Quantity delta check
            if a_qty > 0:
                qty_delta = c_qty - a_qty
                qty_delta_pct = (qty_delta / a_qty) * 100
            elif c_qty > 0:
                qty_delta = c_qty
                qty_delta_pct = 100.0
            else:
                qty_delta = 0
                qty_delta_pct = 0.0

            if abs(qty_delta_pct) >= QUANTITY_DELTA_THRESHOLD_PCT:
                gaps.append({
                    "gap_type": "quantity_delta",
                    "category": c_item.get("category", ""),
                    "description": c_item.get("description", ""),
                    "contractor_qty": c_qty,
                    "adjuster_qty": a_qty,
                    "quantity_delta": round(qty_delta, 2),
                    "quantity_delta_pct": round(qty_delta_pct, 2),
                    "contractor_total": round(c_total, 2),
                    "adjuster_total": round(a_total, 2),
                    "pricing_delta": None,
                    "trade": c_item.get("trade", "general"),
                })
                logger.info(
                    "Quantity delta: %s (%s) adj=%s ctr=%s (%.1f%%)",
                    c_item.get("description", ""),
                    c_item.get("category", ""),
                    a_qty, c_qty, qty_delta_pct,
                )

            # Pricing delta check (independent of quantity)
            if a_cost > 0:
                price_delta = c_cost - a_cost
                price_delta_pct = (price_delta / a_cost) * 100
                if abs(price_delta_pct) >= QUANTITY_DELTA_THRESHOLD_PCT:
                    gaps.append({
                        "gap_type": "pricing_delta",
                        "category": c_item.get("category", ""),
                        "description": c_item.get("description", ""),
                        "contractor_qty": c_qty,
                        "adjuster_qty": a_qty,
                        "quantity_delta": None,
                        "quantity_delta_pct": None,
                        "contractor_total": round(c_total, 2),
                        "adjuster_total": round(a_total, 2),
                        "pricing_delta": round(price_delta, 2),
                        "trade": c_item.get("trade", "general"),
                    })

    logger.info(
        "Diff complete: %d gaps found (%d missing, %d qty deltas, %d price deltas)",
        len(gaps),
        sum(1 for g in gaps if g["gap_type"] == "missing_item"),
        sum(1 for g in gaps if g["gap_type"] == "quantity_delta"),
        sum(1 for g in gaps if g["gap_type"] == "pricing_delta"),
    )

    return gaps
