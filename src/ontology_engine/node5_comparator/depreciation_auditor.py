"""
Depreciation Auditor — TASK_I4

Validates depreciation percentages applied by the adjuster against
reasonable age/life ratios. Flags excessive depreciation that may
represent recoverable amounts upon completion of repairs.

Industry Context:
    Xactimate adjusters apply depreciation based on item age vs expected
    useful life. Common abuses include over-depreciating items like
    paint (expected 3-5 yr life) or carpet (8-10 yr life).

    Depreciation > 50% on most items is worth auditing.
    Depreciation > 70% should be flagged for review.
"""

import logging

logger = logging.getLogger(__name__)

# Depreciation thresholds for flagging
DEPRECIATION_WARNING_PCT = 50.0   # Audit recommended
DEPRECIATION_CRITICAL_PCT = 70.0  # Flag for mandatory review

# Known reasonable depreciation ranges by category keyword
# Format: keyword → max expected depreciation %
DEPRECIATION_GUIDELINES: dict[str, float] = {
    "paint": 40.0,
    "carpet": 50.0,
    "drywall": 30.0,
    "roofing": 40.0,
    "shingle": 40.0,
    "siding": 35.0,
    "gutter": 35.0,
    "window": 30.0,
    "door": 30.0,
    "plumbing": 25.0,
    "electrical": 25.0,
    "hvac": 35.0,
    "flooring": 45.0,
    "insulation": 20.0,
    "fence": 40.0,
}


def _get_guideline_max(description: str, category: str) -> float | None:
    """Look up the expected max depreciation for an item.

    Args:
        description: Line item description
        category: Xactimate category code

    Returns:
        Maximum expected depreciation %, or None if no guideline found
    """
    text = f"{description} {category}".lower()
    for keyword, max_pct in DEPRECIATION_GUIDELINES.items():
        if keyword in text:
            return max_pct
    return None


def audit_depreciation(
    adjuster_items: list[dict],
    adjuster_totals: dict,
) -> list[dict]:
    """Audit depreciation applied by the adjuster.

    Examines each line item's implied depreciation and flags items
    where the depreciation percentage appears excessive.

    Since Node 3 output has adjusted_totals with aggregate depreciation
    but line items may not carry per-item depreciation, we also check
    the aggregate depreciation ratio.

    Args:
        adjuster_items: procurement_items from adjuster estimate
        adjuster_totals: adjusted_totals from adjuster estimate

    Returns:
        List of depreciation finding dicts conforming to
        NODE_5_OUTPUT_SCHEMA.depreciation_findings
    """
    findings: list[dict] = []

    # Check aggregate depreciation ratio
    rcv = adjuster_totals.get("rcv", 0)
    depreciation = adjuster_totals.get("depreciation", 0)

    if rcv > 0 and depreciation > 0:
        aggregate_pct = (depreciation / rcv) * 100

        if aggregate_pct >= DEPRECIATION_WARNING_PCT:
            flagged = aggregate_pct >= DEPRECIATION_CRITICAL_PCT
            flag_reason = ""
            if flagged:
                flag_reason = (
                    f"Aggregate depreciation {aggregate_pct:.1f}% exceeds "
                    f"critical threshold ({DEPRECIATION_CRITICAL_PCT}%)"
                )
            else:
                flag_reason = (
                    f"Aggregate depreciation {aggregate_pct:.1f}% exceeds "
                    f"warning threshold ({DEPRECIATION_WARNING_PCT}%)"
                )

            findings.append({
                "category": "AGGREGATE",
                "description": "Overall estimate depreciation",
                "depreciation_pct": round(aggregate_pct, 2),
                "flagged": flagged,
                "flag_reason": flag_reason,
                "recoverable_amount": round(depreciation, 2),
            })
            logger.info(
                "Aggregate depreciation: %.1f%% ($%.2f of $%.2f RCV)",
                aggregate_pct, depreciation, rcv,
            )

    # Check per-item depreciation if items have depreciation data
    for item in adjuster_items:
        item_deprec = item.get("depreciation", 0)
        item_total = item.get("unit_cost", 0) * item.get("physical_qty", 0)

        if item_total > 0 and item_deprec > 0:
            item_pct = (item_deprec / item_total) * 100
            description = item.get("description", "")
            category = item.get("category", "")

            guideline_max = _get_guideline_max(description, category)
            flagged = False
            flag_reason = ""

            if guideline_max and item_pct > guideline_max:
                flagged = True
                flag_reason = (
                    f"Depreciation {item_pct:.1f}% exceeds guideline maximum "
                    f"{guideline_max:.0f}% for {description}"
                )
            elif item_pct >= DEPRECIATION_CRITICAL_PCT:
                flagged = True
                flag_reason = (
                    f"Depreciation {item_pct:.1f}% exceeds critical threshold "
                    f"({DEPRECIATION_CRITICAL_PCT}%)"
                )
            elif item_pct >= DEPRECIATION_WARNING_PCT:
                flag_reason = (
                    f"Depreciation {item_pct:.1f}% exceeds warning threshold "
                    f"({DEPRECIATION_WARNING_PCT}%)"
                )

            if item_pct >= DEPRECIATION_WARNING_PCT or flagged:
                findings.append({
                    "category": category,
                    "description": description,
                    "depreciation_pct": round(item_pct, 2),
                    "flagged": flagged,
                    "flag_reason": flag_reason,
                    "recoverable_amount": round(item_deprec, 2),
                })
                logger.info(
                    "Depreciation finding: %s (%s) — %.1f%% ($%.2f)",
                    description, category, item_pct, item_deprec,
                )

    logger.info("Depreciation audit complete: %d findings", len(findings))
    return findings
