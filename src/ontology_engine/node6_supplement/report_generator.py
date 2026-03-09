"""
Report Generator — Main Node 6 Orchestrator

Coordinates the report generation process:
  1. Validate Node 5 input
  2. Format category narratives (narrative_formatter)
  3. Summarize financials (dollar_summarizer)
  4. Build O&P and depreciation narratives
  5. Generate recommended actions
  6. Assemble final report conforming to NODE_6_REPORT_SCHEMA

Design by Contract:
  Input:  NODE_5_OUTPUT_SCHEMA (gap report from comparator)
  Output: NODE_6_REPORT_SCHEMA (supplement report)
"""

import logging
from datetime import datetime, timezone

from .narrative_formatter import (
    format_category_narratives,
    format_executive_narrative,
)
from .dollar_summarizer import (
    summarize_financials,
    format_op_narrative,
    format_depreciation_narrative,
    build_recommended_actions,
)

logger = logging.getLogger(__name__)


def generate_supplement_report(
    gap_report: dict,
    *,
    report_id: str | None = None,
) -> dict:
    """Generate a supplement report from a Node 5 gap report.

    Args:
        gap_report: Node 5 output conforming to NODE_5_OUTPUT_SCHEMA.
            Must contain: summary, line_item_gaps, op_analysis,
            depreciation_findings.
        report_id: Optional identifier for cross-referencing.

    Returns:
        Supplement report dict conforming to NODE_6_REPORT_SCHEMA.

    Raises:
        ValueError: If gap_report is missing required keys.
    """
    # Validate required keys
    required_keys = ["summary", "line_item_gaps", "op_analysis", "depreciation_findings"]
    missing = [k for k in required_keys if k not in gap_report]
    if missing:
        raise ValueError(
            f"Gap report missing required keys: {missing}. "
            f"Expected NODE_5_OUTPUT_SCHEMA format."
        )

    summary = gap_report["summary"]
    line_item_gaps = gap_report["line_item_gaps"]
    op_analysis = gap_report["op_analysis"]
    depreciation_findings = gap_report["depreciation_findings"]

    logger.info(
        "Generating supplement report: %d gaps, delta=$%.2f",
        summary.get("gap_count", len(line_item_gaps)),
        summary.get("total_delta", 0),
    )

    # 1. Format category narratives (TASK_J2)
    category_narratives = format_category_narratives(line_item_gaps)

    # 2. Summarize financials (TASK_J3)
    financial_summary = summarize_financials(
        category_narratives, op_analysis, depreciation_findings
    )

    # 3. O&P narrative
    op_narrative = format_op_narrative(op_analysis)

    # 4. Depreciation narrative
    depreciation_narrative = format_depreciation_narrative(depreciation_findings)

    # 5. Recommended actions
    recommended_actions = build_recommended_actions(
        category_narratives, op_narrative, depreciation_narrative, financial_summary
    )

    # 6. Executive summary
    total_recovery = financial_summary["total_recovery"]
    gap_count = summary.get("gap_count", len(line_item_gaps))

    executive_narrative = format_executive_narrative(
        summary, total_recovery, gap_count
    )

    executive_summary = {
        "total_recovery_estimate": total_recovery,
        "adjuster_rcv": summary.get("adjuster_rcv", 0),
        "contractor_rcv": summary.get("contractor_rcv", 0),
        "total_delta": summary.get("total_delta", 0),
        "gap_count": gap_count,
        "narrative": executive_narrative,
    }

    # 7. Report metadata
    report_metadata = {
        "report_type": "supplement_report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_gap_report_id": report_id,
        "claim_number": summary.get("claim_number"),
        "estimate_number": summary.get("estimate_number"),
        "carrier": summary.get("carrier"),
    }

    report = {
        "report_metadata": report_metadata,
        "executive_summary": executive_summary,
        "category_narratives": category_narratives,
        "financial_summary": financial_summary,
        "op_narrative": op_narrative,
        "depreciation_narrative": depreciation_narrative,
        "recommended_actions": recommended_actions,
    }

    logger.info(
        "Supplement report generated: total_recovery=$%.2f, "
        "%d categories, %d recommended actions",
        total_recovery,
        len(category_narratives),
        len(recommended_actions),
    )

    return report
