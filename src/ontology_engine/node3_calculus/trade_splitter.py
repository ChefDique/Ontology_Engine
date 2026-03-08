"""
Trade Splitter — TASK_B7

Splits multi-trade estimates into separate payloads by trade category.
A single Xactimate estimate may contain RFG (roofing), SID (siding),
DRY (drywall) — each destined for different suppliers.
"""

from ..node2_extraction.lexicon_matrix import lookup_code


def split_by_trade(line_items: list[dict]) -> dict[str, list[dict]]:
    """Split line items into trade-specific groups.

    Uses the Lexicon Matrix to determine trade classification for each
    category code. Items with unknown codes are grouped under 'general'.

    Args:
        line_items: list of dicts with at least a 'category' field.

    Returns:
        dict mapping trade name → list of line items for that trade.
        Example: {"roofing": [...], "siding": [...], "electrical": [...]}
    """
    trades: dict[str, list[dict]] = {}

    for item in line_items:
        category = item.get("category", "")
        lexicon_entry = lookup_code(category)

        # Use lexicon trade or check if item already has trade assigned
        trade = (
            lexicon_entry["trade"]
            if lexicon_entry
            else item.get("trade", "general")
        )

        if trade not in trades:
            trades[trade] = []
        trades[trade].append(item)

    return trades
