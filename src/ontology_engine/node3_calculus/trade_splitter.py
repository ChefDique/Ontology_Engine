"""
Trade Splitter — TASK_B7

Splits multi-trade estimates into separate payloads by trade category.
A single Xactimate estimate may contain RFG (roofing), SID (siding),
DRY (drywall) — each destined for different suppliers.
"""


def split_by_trade(line_items: list[dict]) -> dict[str, list[dict]]:
    """Split line items into trade-specific groups.

    Returns: dict mapping trade name → list of line items for that trade.
    """
    raise NotImplementedError("TASK_B7: Multi-trade data splitting")
