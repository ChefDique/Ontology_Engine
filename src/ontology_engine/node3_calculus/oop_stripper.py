"""
O&P Stripper — TASK_B4

Strips Overhead & Profit (O&P) margins from Xactimate totals
before CRM injection to prevent double-taxation (CONST_002).

Design by Contract:
  Invariant: O&P NEVER applied twice. Node 3 strips O&P;
             CRM applies its own independently.
"""

from decimal import Decimal, ROUND_HALF_UP


def strip_overhead_and_profit(totals: dict, line_items: list[dict]) -> dict:
    """Remove O&P from Xactimate financial totals.

    Xactimate typically applies 10% Overhead + 10% Profit on top of
    the RCV (Replacement Cost Value). Tax is also recalculated on the
    stripped amount.

    Uses Decimal arithmetic to prevent floating-point rounding errors
    in currency calculations.

    Args:
        totals: dict with keys rcv, depreciation, acv, overhead, profit, tax, net_claim
        line_items: list of extracted line items (used for line-level adjustments)

    Returns:
        dict with keys:
            - adjusted_totals: dict (totals with O&P removed)
            - stripped_overhead: float
            - stripped_profit: float
            - stripped_tax_adjustment: float
            - note: str ("O&P stripped")
    """
    # Convert to Decimal for precise currency math
    rcv = Decimal(str(totals.get("rcv", 0)))
    depreciation = Decimal(str(totals.get("depreciation", 0)))
    overhead = Decimal(str(totals.get("overhead", 0)))
    profit = Decimal(str(totals.get("profit", 0)))
    tax = Decimal(str(totals.get("tax", 0)))
    net_claim = Decimal(str(totals.get("net_claim", 0)))

    # Strip O&P: subtract overhead and profit from totals
    adjusted_rcv = rcv - overhead - profit
    adjusted_acv = adjusted_rcv - depreciation

    # Recalculate tax on the adjusted amount
    # Tax rate = original_tax / original_rcv (if rcv > 0)
    if rcv > 0 and tax > 0:
        tax_rate = tax / rcv
        adjusted_tax = (adjusted_rcv * tax_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        tax_adjustment = tax - adjusted_tax
    else:
        adjusted_tax = tax
        tax_adjustment = Decimal("0")

    adjusted_net = adjusted_acv + adjusted_tax

    # Build result with float outputs for JSON serialization
    return {
        "adjusted_totals": {
            "rcv": float(adjusted_rcv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "depreciation": float(depreciation.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "acv": float(adjusted_acv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "overhead": 0.0,
            "profit": 0.0,
            "tax": float(adjusted_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "net_claim": float(adjusted_net.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        },
        "stripped_overhead": float(overhead.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "stripped_profit": float(profit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "stripped_tax_adjustment": float(tax_adjustment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "note": "O&P stripped",
    }
