"""
TASK_J3 — Dollar-Impact Summarizer

Aggregates financial impact from three sources:
  1. Line-item gaps (missing items, quantity deltas, pricing deltas)
  2. O&P recovery (overhead & profit warranted but not applied)
  3. Depreciation audit (excessive depreciation on specific items)

Produces per-category breakdowns and total recovery estimates.
"""

import logging

logger = logging.getLogger(__name__)


def summarize_financials(
    category_narratives: list[dict],
    op_analysis: dict,
    depreciation_findings: list[dict],
) -> dict:
    """Build full financial summary from gap report components.

    Args:
        category_narratives: Output of format_category_narratives.
        op_analysis: Node 5 op_analysis dict.
        depreciation_findings: Node 5 depreciation_findings list.

    Returns:
        Financial summary dict conforming to NODE_6_REPORT_SCHEMA.financial_summary.
    """
    # 1. Sum line-item recovery by category
    line_item_recovery = 0.0
    by_category = []

    for cat in category_narratives:
        amount = cat.get("total_impact", 0)
        line_item_recovery += amount
        by_category.append({
            "category": cat["category"],
            "category_label": cat["category_label"],
            "amount": round(amount, 2),
            "pct_of_total": 0.0,  # Computed after totals are known
        })

    line_item_recovery = round(line_item_recovery, 2)

    # 2. O&P recovery
    op_recovery = round(op_analysis.get("op_recovery_amount", 0), 2)
    if op_recovery > 0:
        by_category.append({
            "category": "O&P",
            "category_label": "Overhead & Profit",
            "amount": op_recovery,
            "pct_of_total": 0.0,
        })

    # 3. Depreciation recovery
    depreciation_recovery = 0.0
    for finding in depreciation_findings:
        if finding.get("flagged", False):
            recoverable = finding.get("recoverable_amount")
            if recoverable is not None and recoverable > 0:
                depreciation_recovery += recoverable

    depreciation_recovery = round(depreciation_recovery, 2)
    if depreciation_recovery > 0:
        by_category.append({
            "category": "DEP",
            "category_label": "Depreciation Recovery",
            "amount": depreciation_recovery,
            "pct_of_total": 0.0,
        })

    # 4. Total
    total_recovery = round(
        line_item_recovery + op_recovery + depreciation_recovery, 2
    )

    # 5. Compute percentages
    for entry in by_category:
        if total_recovery > 0:
            entry["pct_of_total"] = round(
                (entry["amount"] / total_recovery) * 100, 1
            )

    # Sort by amount descending
    by_category.sort(key=lambda x: x["amount"], reverse=True)

    return {
        "line_item_recovery": line_item_recovery,
        "op_recovery": op_recovery,
        "depreciation_recovery": depreciation_recovery,
        "total_recovery": total_recovery,
        "by_category": by_category,
    }


def format_op_narrative(op_analysis: dict) -> dict:
    """Generate the O&P narrative section.

    Args:
        op_analysis: Node 5 op_analysis dict with trade_count,
                     op_warranted, adjuster_op_applied, etc.

    Returns:
        O&P narrative dict for the report.
    """
    trade_count = op_analysis.get("trade_count", 0)
    warranted = op_analysis.get("op_warranted", False)
    trades = op_analysis.get("trades_detected", [])
    recovery = round(op_analysis.get("op_recovery_amount", 0), 2)
    adj_op = op_analysis.get("adjuster_op_applied", {})
    ctr_op = op_analysis.get("contractor_op_applied", {})

    if warranted:
        adj_oh = adj_op.get("overhead", 0)
        adj_pr = adj_op.get("profit", 0)
        narrative = (
            f"Overhead & Profit is warranted for this claim. "
            f"{trade_count} distinct trades were identified "
            f"({', '.join(trades)}), exceeding the standard 3-trade "
            f"threshold. The adjuster's estimate applied "
            f"${adj_oh:,.2f} overhead and ${adj_pr:,.2f} profit, while "
            f"the contractor's estimate reflects standard 10/10 O&P. "
            f"The estimated O&P recovery is ${recovery:,.2f}."
        )
    else:
        if trade_count > 0:
            narrative = (
                f"Overhead & Profit may not be warranted based on current "
                f"trade count. Only {trade_count} trade{'s were' if trade_count > 1 else ' was'} "
                f"identified ({', '.join(trades) if trades else 'none'}), "
                f"which falls below the standard 3-trade threshold."
            )
        else:
            narrative = (
                "No distinct trades were identified for O&P analysis."
            )

    return {
        "applicable": warranted,
        "trade_count": trade_count,
        "trades": trades,
        "recovery_amount": recovery,
        "narrative": narrative,
    }


def format_depreciation_narrative(depreciation_findings: list[dict]) -> dict:
    """Generate the depreciation narrative section.

    Args:
        depreciation_findings: Node 5 depreciation_findings list.

    Returns:
        Depreciation narrative dict for the report.
    """
    flagged = [f for f in depreciation_findings if f.get("flagged", False)]
    total_recoverable = 0.0
    formatted_findings = []

    for finding in flagged:
        recoverable = finding.get("recoverable_amount")
        if recoverable is not None and recoverable > 0:
            total_recoverable += recoverable

        formatted_findings.append({
            "description": finding.get("description", "Unknown item"),
            "depreciation_pct": finding.get("depreciation_pct", 0),
            "flag_reason": finding.get("flag_reason", ""),
            "recoverable": recoverable,
        })

    total_recoverable = round(total_recoverable, 2)
    has_findings = len(flagged) > 0

    if has_findings:
        sentences = [
            f"The depreciation audit identified {len(flagged)} item"
            f"{'s' if len(flagged) > 1 else ''} with potentially "
            f"excessive depreciation."
        ]
        for f in formatted_findings[:3]:
            sentences.append(
                f'"{f["description"]}" shows {f["depreciation_pct"]:.1f}% '
                f"depreciation — {f['flag_reason']}."
            )
        if total_recoverable > 0:
            sentences.append(
                f"Total estimated depreciation recovery: "
                f"${total_recoverable:,.2f}."
            )
        narrative = " ".join(sentences)
    else:
        narrative = (
            "No items with excessive depreciation were identified. "
            "All depreciation rates fall within standard guidelines."
        )

    return {
        "has_findings": has_findings,
        "finding_count": len(flagged),
        "total_recoverable": total_recoverable,
        "findings": formatted_findings,
        "narrative": narrative,
    }


def build_recommended_actions(
    category_narratives: list[dict],
    op_narrative: dict,
    depreciation_narrative: dict,
    financial_summary: dict,
) -> list[dict]:
    """Generate prioritized recommended actions.

    Actions are ordered by expected recovery amount (highest first).

    Args:
        category_narratives: Formatted category narratives.
        op_narrative: Formatted O&P narrative.
        depreciation_narrative: Formatted depreciation narrative.
        financial_summary: Financial summary dict.

    Returns:
        List of action dicts with priority, action, expected_recovery, rationale.
    """
    actions = []

    # O&P recovery action (usually the biggest win)
    if op_narrative.get("applicable", False):
        recovery = op_narrative.get("recovery_amount", 0)
        if recovery > 0:
            trades = op_narrative.get("trades", [])
            actions.append({
                "priority": 0,  # Will be re-numbered
                "action": (
                    f"Submit O&P supplement — {op_narrative.get('trade_count', 0)} "
                    f"trades warrant 10/10 overhead & profit"
                ),
                "category": "O&P",
                "expected_recovery": recovery,
                "rationale": (
                    f"Trades identified: {', '.join(trades)}. "
                    f"Adjuster applied 0% O&P despite meeting the "
                    f"3-trade threshold."
                ),
            })

    # Category-specific actions (top 5 by impact)
    for cat in category_narratives[:5]:
        if cat["total_impact"] > 0:
            missing_count = sum(
                1 for g in cat.get("gaps", [])
                if g.get("gap_type") == "missing_item"
            )
            qty_count = sum(
                1 for g in cat.get("gaps", [])
                if g.get("gap_type") == "quantity_delta"
            )
            detail_parts = []
            if missing_count > 0:
                detail_parts.append(f"{missing_count} missing items")
            if qty_count > 0:
                detail_parts.append(f"{qty_count} quantity discrepancies")
            detail = ", ".join(detail_parts) if detail_parts else "pricing adjustments"

            actions.append({
                "priority": 0,
                "action": (
                    f"Supplement {cat['category_label']} scope — "
                    f"{detail}"
                ),
                "category": cat["category"],
                "expected_recovery": cat["total_impact"],
                "rationale": cat["narrative"][:200],
            })

    # Depreciation action
    if depreciation_narrative.get("has_findings", False):
        total_dep = depreciation_narrative.get("total_recoverable", 0)
        if total_dep > 0:
            actions.append({
                "priority": 0,
                "action": (
                    f"Challenge depreciation on "
                    f"{depreciation_narrative.get('finding_count', 0)} items"
                ),
                "category": "DEP",
                "expected_recovery": total_dep,
                "rationale": depreciation_narrative["narrative"][:200],
            })

    # Sort by expected recovery descending, assign priorities
    actions.sort(key=lambda x: x["expected_recovery"], reverse=True)
    for i, action in enumerate(actions):
        action["priority"] = i + 1

    return actions
