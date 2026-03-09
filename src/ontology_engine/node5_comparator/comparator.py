"""
Comparator — Main Node 5 Orchestrator

Coordinates the three analysis engines:
  1. Line-item diff (diff_engine) — missing items, qty/price deltas
  2. O&P detection (op_detector) — trade count → warranted vs applied
  3. Depreciation audit (depreciation_auditor) — age/life ratio validation

Produces a unified gap report conforming to NODE_5_OUTPUT_SCHEMA.

Design by Contract:
  Input:  Two NODE_3_TO_4 payloads (adjuster + contractor)
  Output: Structured gap report (summary + line_item_gaps + op_analysis + depreciation_findings)
"""

import logging

from .diff_engine import diff_line_items
from .op_detector import analyze_op
from .depreciation_auditor import audit_depreciation

logger = logging.getLogger(__name__)


def compare_estimates(
    adjuster_estimate: dict,
    contractor_estimate: dict,
) -> dict:
    """Compare two estimates and produce a gap report.

    Both inputs should be Node 3→4 output format (the result of running
    each PDF through the Ingestion → Extraction → Calculus pipeline).

    Args:
        adjuster_estimate: Node 3 output for the insurance adjuster's estimate
        contractor_estimate: Node 3 output for the contractor's estimate

    Returns:
        Gap report dict conforming to NODE_5_OUTPUT_SCHEMA with keys:
            - summary: high-level financial comparison
            - line_item_gaps: detailed per-item differences
            - op_analysis: O&P warranted vs applied analysis
            - depreciation_findings: items with questionable depreciation
    """
    adj_items = adjuster_estimate.get("procurement_items", [])
    ctr_items = contractor_estimate.get("procurement_items", [])
    adj_totals = adjuster_estimate.get("adjusted_totals", {})
    ctr_totals = contractor_estimate.get("adjusted_totals", {})

    # 1. Line-item diff
    line_item_gaps = diff_line_items(adj_items, ctr_items)

    # 2. O&P analysis
    op_analysis = analyze_op(adjuster_estimate, contractor_estimate)

    # 3. Depreciation audit (on adjuster's estimate only)
    depreciation_findings = audit_depreciation(adj_items, adj_totals)

    # 4. Build summary
    adj_rcv = adj_totals.get("rcv", 0)
    ctr_rcv = ctr_totals.get("rcv", 0)
    total_delta = round(ctr_rcv - adj_rcv, 2)

    summary = {
        "adjuster_rcv": adj_rcv,
        "contractor_rcv": ctr_rcv,
        "total_delta": total_delta,
        "gap_count": len(line_item_gaps),
        "adjuster_line_count": len(adj_items),
        "contractor_line_count": len(ctr_items),
    }

    logger.info(
        "Comparison complete: adjuster RCV=$%.2f, contractor RCV=$%.2f, "
        "delta=$%.2f, %d line-item gaps, O&P recovery=$%.2f, "
        "%d depreciation findings",
        adj_rcv, ctr_rcv, total_delta,
        len(line_item_gaps),
        op_analysis.get("op_recovery_amount", 0),
        len(depreciation_findings),
    )

    return {
        "summary": summary,
        "line_item_gaps": line_item_gaps,
        "op_analysis": op_analysis,
        "depreciation_findings": depreciation_findings,
    }
