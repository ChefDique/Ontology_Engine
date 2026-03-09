"""
O&P Detection — TASK_I3

Determines whether Overhead & Profit (O&P) is warranted based on
Xactimate's "3-trade rule" and calculates the recovery amount when
the adjuster failed to apply warranted O&P.

Industry Standard (Xactimate):
    O&P is warranted when 3+ distinct trades are involved in the loss.
    Typical rate: 10% overhead + 10% profit on RCV.

The adjuster's adjusted_totals already have O&P stripped by Node 3.
We compare the ORIGINAL totals to detect if O&P was applied.
"""

import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# O&P is warranted when this many or more distinct trades are present
OP_WARRANTED_TRADE_THRESHOLD = 3

# Standard O&P rates (10/10 is industry standard)
DEFAULT_OVERHEAD_RATE = Decimal("0.10")
DEFAULT_PROFIT_RATE = Decimal("0.10")


def detect_trades(procurement_items: list[dict]) -> list[str]:
    """Extract distinct trade categories from procurement items.

    Args:
        procurement_items: Line items with 'trade' field.

    Returns:
        Sorted list of unique trade names.
    """
    trades = set()
    for item in procurement_items:
        trade = item.get("trade", "general")
        if trade and trade.lower() != "general":
            trades.add(trade.lower())

    # If we only found 'general' or nothing, still count it
    if not trades:
        trades.add("general")

    return sorted(trades)


def analyze_op(
    adjuster_estimate: dict,
    contractor_estimate: dict,
) -> dict:
    """Analyze O&P application across both estimates.

    Compares trade count against the 3-trade threshold, then
    calculates the O&P recovery amount if adjuster under-applied.

    Args:
        adjuster_estimate: Full Node 3 output (adjuster side)
        contractor_estimate: Full Node 3 output (contractor side)

    Returns:
        dict conforming to NODE_5_OUTPUT_SCHEMA.op_analysis
    """
    # Count trades from BOTH estimates (union of trades)
    adj_items = adjuster_estimate.get("procurement_items", [])
    ctr_items = contractor_estimate.get("procurement_items", [])

    adj_trades = detect_trades(adj_items)
    ctr_trades = detect_trades(ctr_items)
    all_trades = sorted(set(adj_trades) | set(ctr_trades))
    trade_count = len(all_trades)

    op_warranted = trade_count >= OP_WARRANTED_TRADE_THRESHOLD

    # Extract O&P amounts from adjusted_totals
    adj_totals = adjuster_estimate.get("adjusted_totals", {})
    ctr_totals = contractor_estimate.get("adjusted_totals", {})

    adj_overhead = adj_totals.get("overhead", 0)
    adj_profit = adj_totals.get("profit", 0)
    ctr_overhead = ctr_totals.get("overhead", 0)
    ctr_profit = ctr_totals.get("profit", 0)

    # Calculate recovery: if O&P is warranted but adjuster didn't apply it
    op_recovery = Decimal("0")
    if op_warranted and (adj_overhead == 0 and adj_profit == 0):
        # Calculate what O&P _should be_ on the adjuster's RCV
        adj_rcv = Decimal(str(adj_totals.get("rcv", 0)))
        warranted_overhead = (adj_rcv * DEFAULT_OVERHEAD_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        warranted_profit = (adj_rcv * DEFAULT_PROFIT_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        op_recovery = warranted_overhead + warranted_profit
        logger.info(
            "O&P recovery opportunity: %d trades detected, warranted O&P = $%.2f "
            "(OH $%.2f + PR $%.2f) on RCV $%.2f",
            trade_count,
            float(op_recovery),
            float(warranted_overhead),
            float(warranted_profit),
            float(adj_rcv),
        )
    elif op_warranted:
        # O&P warranted and applied — check if under-applied
        adj_rcv = Decimal(str(adj_totals.get("rcv", 0)))
        warranted_total = adj_rcv * (DEFAULT_OVERHEAD_RATE + DEFAULT_PROFIT_RATE)
        actual_total = Decimal(str(adj_overhead)) + Decimal(str(adj_profit))
        if warranted_total > actual_total:
            op_recovery = (warranted_total - actual_total).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            logger.info(
                "O&P under-applied: warranted $%.2f vs applied $%.2f = recovery $%.2f",
                float(warranted_total), float(actual_total), float(op_recovery),
            )

    logger.info(
        "O&P analysis: %d trades (%s), warranted=%s, recovery=$%.2f",
        trade_count,
        ", ".join(all_trades),
        op_warranted,
        float(op_recovery),
    )

    return {
        "trade_count": trade_count,
        "op_warranted": op_warranted,
        "adjuster_op_applied": {
            "overhead": adj_overhead,
            "profit": adj_profit,
        },
        "contractor_op_applied": {
            "overhead": ctr_overhead,
            "profit": ctr_profit,
        },
        "op_recovery_amount": float(op_recovery),
        "trades_detected": all_trades,
    }
