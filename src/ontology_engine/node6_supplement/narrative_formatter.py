"""
TASK_J2 — Gap-to-Narrative Formatter

Converts structured gap data from Node 5 into human-readable narratives
organized by category. Each category gets a prose description suitable
for insurance supplement submission.

Category codes follow Xactimate conventions:
    RFG = Roofing, SID = Siding, DRY = Drywall, PNT = Painting,
    FLR = Flooring, ELC = Electrical, PLM = Plumbing, MCA = HVAC,
    GTR = Gutters, CNT = General Conditions, INS = Insulation, etc.
"""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Human-readable labels for Xactimate category codes
CATEGORY_LABELS = {
    "RFG": "Roofing",
    "SID": "Siding",
    "DRY": "Drywall",
    "PNT": "Painting",
    "FLR": "Flooring",
    "ELC": "Electrical",
    "PLM": "Plumbing",
    "MCA": "HVAC / Mechanical",
    "GTR": "Gutters",
    "CNT": "General Conditions",
    "INS": "Insulation",
    "INT": "Interior",
    "EXT": "Exterior",
    "WTR": "Water Damage",
    "DMO": "Demolition",
    "CLN": "Cleaning",
    "FNC": "Fencing",
    "LND": "Landscaping",
    "GNL": "General",
}


def get_category_label(code: str) -> str:
    """Get human-readable label for a category code."""
    return CATEGORY_LABELS.get(code, code)


def _format_gap_detail(gap: dict) -> str:
    """Format a single gap into a human-readable detail string.

    Args:
        gap: A gap dict from Node 5 line_item_gaps.

    Returns:
        A descriptive string for this gap.
    """
    gap_type = gap.get("gap_type", "unknown")
    description = gap.get("description", "Unknown item")

    if gap_type == "missing_item":
        ctr_total = gap.get("contractor_total")
        if ctr_total is not None:
            return (
                f"Missing item: \"{description}\" — present in contractor's "
                f"estimate at ${ctr_total:,.2f} but absent from adjuster's estimate."
            )
        return (
            f"Missing item: \"{description}\" — present in contractor's "
            f"estimate but absent from adjuster's estimate."
        )

    elif gap_type == "quantity_delta":
        adj_qty = gap.get("adjuster_qty")
        ctr_qty = gap.get("contractor_qty")
        delta_pct = gap.get("quantity_delta_pct")
        unit = gap.get("physical_unit", "units")

        parts = [f"Quantity discrepancy: \"{description}\""]
        if adj_qty is not None and ctr_qty is not None:
            parts.append(
                f" — adjuster measured {adj_qty} {unit}, "
                f"contractor measured {ctr_qty} {unit}"
            )
        if delta_pct is not None:
            parts.append(f" ({delta_pct:+.0f}% difference)")
        parts.append(".")
        return "".join(parts)

    elif gap_type == "pricing_delta":
        adj_total = gap.get("adjuster_total")
        ctr_total = gap.get("contractor_total")
        pricing_delta = gap.get("pricing_delta")

        parts = [f"Pricing discrepancy: \"{description}\""]
        if adj_total is not None and ctr_total is not None:
            parts.append(
                f" — adjuster priced at ${adj_total:,.2f}, "
                f"contractor priced at ${ctr_total:,.2f}"
            )
        if pricing_delta is not None:
            parts.append(f" (delta: ${pricing_delta:,.2f})")
        parts.append(".")
        return "".join(parts)

    else:
        return f"Discrepancy: \"{description}\" — type: {gap_type}."


def _compute_gap_impact(gap: dict) -> float:
    """Compute the dollar impact of a single gap.

    Args:
        gap: A gap dict from Node 5 line_item_gaps.

    Returns:
        Dollar impact (positive = money left on table).
    """
    gap_type = gap.get("gap_type", "unknown")

    if gap_type == "missing_item":
        return gap.get("contractor_total", 0) or 0

    elif gap_type == "quantity_delta":
        # Impact = contractor_total - adjuster_total (if both exist)
        ctr = gap.get("contractor_total")
        adj = gap.get("adjuster_total")
        if ctr is not None and adj is not None:
            return max(0, ctr - adj)
        return 0

    elif gap_type == "pricing_delta":
        return abs(gap.get("pricing_delta", 0) or 0)

    return 0


def format_category_narratives(line_item_gaps: list[dict]) -> list[dict]:
    """Group gaps by category and generate narratives.

    Args:
        line_item_gaps: List of gap dicts from NODE_5_OUTPUT_SCHEMA.

    Returns:
        List of category narrative dicts with:
            - category: code
            - category_label: human name
            - gap_count: number of gaps
            - total_impact: dollar sum
            - gaps: list of formatted gap details
            - narrative: prose paragraph
    """
    # Group gaps by category
    by_category = defaultdict(list)
    for gap in line_item_gaps:
        cat = gap.get("category", "GNL")
        by_category[cat].append(gap)

    results = []
    for cat_code, gaps in sorted(by_category.items()):
        cat_label = get_category_label(cat_code)
        formatted_gaps = []
        total_impact = 0.0

        for gap in gaps:
            impact = _compute_gap_impact(gap)
            total_impact += impact
            formatted_gaps.append({
                "gap_type": gap.get("gap_type", "unknown"),
                "description": gap.get("description", "Unknown"),
                "impact": round(impact, 2),
                "detail": _format_gap_detail(gap),
            })

        total_impact = round(total_impact, 2)

        # Build narrative paragraph
        narrative = _build_category_narrative(
            cat_label, cat_code, gaps, formatted_gaps, total_impact
        )

        results.append({
            "category": cat_code,
            "category_label": cat_label,
            "gap_count": len(gaps),
            "total_impact": total_impact,
            "gaps": formatted_gaps,
            "narrative": narrative,
        })

    # Sort by impact descending (highest recovery opportunity first)
    results.sort(key=lambda x: x["total_impact"], reverse=True)
    return results


def _build_category_narrative(
    cat_label: str,
    cat_code: str,
    raw_gaps: list[dict],
    formatted_gaps: list[dict],
    total_impact: float,
) -> str:
    """Build a prose narrative for a single category.

    Args:
        cat_label: Human-readable category name.
        cat_code: Xactimate category code.
        raw_gaps: Raw gap dicts.
        formatted_gaps: List of formatted gap detail dicts.
        total_impact: Total dollar impact for this category.

    Returns:
        A multi-sentence narrative paragraph.
    """
    missing = [g for g in raw_gaps if g.get("gap_type") == "missing_item"]
    qty_deltas = [g for g in raw_gaps if g.get("gap_type") == "quantity_delta"]
    price_deltas = [g for g in raw_gaps if g.get("gap_type") == "pricing_delta"]

    sentences = []

    # Opening
    sentences.append(
        f"The {cat_label} category shows {len(raw_gaps)} discrepanc"
        f"{'y' if len(raw_gaps) == 1 else 'ies'} "
        f"totaling ${total_impact:,.2f} in potential recovery."
    )

    # Missing items
    if missing:
        items_str = ", ".join(
            f'"{g.get("description", "Unknown")}"' for g in missing[:3]
        )
        if len(missing) > 3:
            items_str += f" and {len(missing) - 3} more"
        sentences.append(
            f"{len(missing)} item{'s are' if len(missing) > 1 else ' is'} "
            f"present in the contractor's estimate but missing from the "
            f"adjuster's estimate: {items_str}."
        )

    # Quantity deltas
    if qty_deltas:
        sentences.append(
            f"{len(qty_deltas)} item{'s have' if len(qty_deltas) > 1 else ' has'} "
            f"quantity discrepancies between the two estimates."
        )

    # Pricing deltas
    if price_deltas:
        sentences.append(
            f"{len(price_deltas)} item{'s show' if len(price_deltas) > 1 else ' shows'} "
            f"pricing differences."
        )

    return " ".join(sentences)


def format_executive_narrative(
    summary: dict,
    total_recovery: float,
    gap_count: int,
) -> str:
    """Generate the executive summary narrative paragraph.

    Args:
        summary: Node 5 summary dict.
        total_recovery: Total projected recovery across all categories.
        gap_count: Total number of gaps identified.

    Returns:
        A prose summary paragraph.
    """
    adj_rcv = summary.get("adjuster_rcv", 0)
    ctr_rcv = summary.get("contractor_rcv", 0)
    delta = summary.get("total_delta", 0)

    return (
        f"This supplement report identifies {gap_count} discrepancies "
        f"between the adjuster's estimate (RCV: ${adj_rcv:,.2f}) and the "
        f"contractor's estimate (RCV: ${ctr_rcv:,.2f}), representing a "
        f"total delta of ${delta:,.2f}. Based on line-item analysis, "
        f"overhead & profit review, and depreciation audit, the estimated "
        f"total recovery opportunity is ${total_recovery:,.2f}. "
        f"The following sections detail each discrepancy category with "
        f"supporting documentation for carrier submission."
    )
