"""
Unit + Integration Tests — Node 6: Supplement Report Generator (TASK_J5)

Uses McKee case study data from Node 5 comparator tests:
  - Adjuster RCV: $63,137.79 (13 representative items)
  - Contractor RCV: $123,219.52 (21 representative items)
  - Delta: $60,081.73
  - 9 trades → O&P warranted, adjuster applied 0%
  - Missing items, quantity deltas, depreciation issues

Test structure:
  1. Fixtures — McKee gap report (output of Node 5)
  2. TASK_J1 tests — Schema validation
  3. TASK_J2 tests — Narrative formatter
  4. TASK_J3 tests — Dollar summarizer
  5. TASK_J5 tests — Full integration (generate_supplement_report)
"""

import pytest
from ontology_engine.node6_supplement.report_generator import generate_supplement_report
from ontology_engine.node6_supplement.narrative_formatter import (
    format_category_narratives,
    format_executive_narrative,
    get_category_label,
    _format_gap_detail,
    _compute_gap_impact,
)
from ontology_engine.node6_supplement.dollar_summarizer import (
    summarize_financials,
    format_op_narrative,
    format_depreciation_narrative,
    build_recommended_actions,
)


# ===========================================================================
# Fixtures — McKee Gap Report (Node 5 output)
# ===========================================================================

@pytest.fixture
def mckee_gap_report():
    """Simulated Node 5 output for the McKee case study."""
    return {
        "summary": {
            "adjuster_rcv": 63137.79,
            "contractor_rcv": 123219.52,
            "total_delta": 60081.73,
            "gap_count": 17,
            "adjuster_line_count": 13,
            "contractor_line_count": 21,
        },
        "line_item_gaps": [
            {"gap_type": "missing_item", "category": "CNT", "description": "Dust barrier - 6 mil poly", "contractor_qty": 200, "adjuster_qty": None, "contractor_total": 170.00, "adjuster_total": None, "trade": "general_conditions"},
            {"gap_type": "missing_item", "category": "CNT", "description": "Floor protection - ram board", "contractor_qty": 150, "adjuster_qty": None, "contractor_total": 187.50, "adjuster_total": None, "trade": "general_conditions"},
            {"gap_type": "missing_item", "category": "CNT", "description": "Pool tarping - protective cover", "contractor_qty": 1, "adjuster_qty": None, "contractor_total": 450.00, "adjuster_total": None, "trade": "general_conditions"},
            {"gap_type": "missing_item", "category": "CNT", "description": "Emergency service call", "contractor_qty": 1, "adjuster_qty": None, "contractor_total": 350.00, "adjuster_total": None, "trade": "general_conditions"},
            {"gap_type": "missing_item", "category": "INS", "description": "Insulation - blown-in R-38", "contractor_qty": 400, "adjuster_qty": None, "contractor_total": 1000.00, "adjuster_total": None, "trade": "insulation"},
            {"gap_type": "missing_item", "category": "ELC", "description": "Can light - remove & reinstall", "contractor_qty": 6, "adjuster_qty": None, "contractor_total": 750.00, "adjuster_total": None, "trade": "electrical"},
            {"gap_type": "missing_item", "category": "RFG", "description": "Ice & water shield", "contractor_qty": 200, "adjuster_qty": None, "contractor_total": 500.00, "adjuster_total": None, "trade": "roofing"},
            {"gap_type": "missing_item", "category": "RFG", "description": "Roof vent - box type", "contractor_qty": 4, "adjuster_qty": None, "contractor_total": 300.00, "adjuster_total": None, "trade": "roofing"},
            {"gap_type": "quantity_delta", "category": "RFG", "description": "Shingle roofing - comp./asphalt (3-tab/25 year)", "contractor_qty": 54, "adjuster_qty": 22, "quantity_delta": 32, "quantity_delta_pct": 145.5, "contractor_total": 10530.00, "adjuster_total": 4070.00, "trade": "roofing"},
            {"gap_type": "quantity_delta", "category": "RFG", "description": "Hip/ridge cap - comp. shingle", "contractor_qty": 66, "adjuster_qty": 32, "quantity_delta": 34, "quantity_delta_pct": 106.3, "contractor_total": 379.50, "adjuster_total": 176.00, "trade": "roofing"},
            {"gap_type": "quantity_delta", "category": "RFG", "description": "Mod bit roof membrane", "contractor_qty": 245, "adjuster_qty": 100, "quantity_delta": 145, "quantity_delta_pct": 145.0, "contractor_total": 3185.00, "adjuster_total": 1250.00, "trade": "roofing"},
            {"gap_type": "quantity_delta", "category": "SID", "description": "Vinyl siding - remove & replace", "contractor_qty": 280, "adjuster_qty": 200, "quantity_delta": 80, "quantity_delta_pct": 40.0, "contractor_total": 2520.00, "adjuster_total": 1750.00, "trade": "siding"},
            {"gap_type": "quantity_delta", "category": "DRY", "description": "Drywall - 1/2\" standard hung, taped, floated", "contractor_qty": 101, "adjuster_qty": 50, "quantity_delta": 51, "quantity_delta_pct": 102.0, "contractor_total": 378.75, "adjuster_total": 175.00, "trade": "drywall"},
            {"gap_type": "quantity_delta", "category": "PNT", "description": "Paint interior walls - 2 coats", "contractor_qty": 350, "adjuster_qty": 200, "quantity_delta": 150, "quantity_delta_pct": 75.0, "contractor_total": 472.50, "adjuster_total": 250.00, "trade": "painting"},
            {"gap_type": "quantity_delta", "category": "FLR", "description": "Carpet - standard grade", "contractor_qty": 45, "adjuster_qty": 30, "quantity_delta": 15, "quantity_delta_pct": 50.0, "contractor_total": 1260.00, "adjuster_total": 750.00, "trade": "flooring"},
            {"gap_type": "quantity_delta", "category": "GTR", "description": "Gutter - aluminum - 5\"", "contractor_qty": 110, "adjuster_qty": 85, "quantity_delta": 25, "quantity_delta_pct": 29.4, "contractor_total": 880.00, "adjuster_total": 637.50, "trade": "gutters"},
            {"gap_type": "pricing_delta", "category": "RFG", "description": "Remove Comp. shingle roofing - 3 tab/25yr", "contractor_qty": 22, "adjuster_qty": 22, "contractor_total": 1100.00, "adjuster_total": 990.00, "pricing_delta": 110.00, "trade": "roofing"},
        ],
        "op_analysis": {
            "trade_count": 9,
            "op_warranted": True,
            "adjuster_op_applied": {"overhead": 0.0, "profit": 0.0},
            "contractor_op_applied": {"overhead": 10321.34, "profit": 10321.34},
            "op_recovery_amount": 12627.56,
            "trades_detected": ["roofing", "siding", "drywall", "painting", "flooring", "electrical", "plumbing", "hvac", "gutters"],
        },
        "depreciation_findings": [
            {"category": "PNT", "description": "Paint interior walls - 2 coats", "depreciation_pct": 46.67, "flagged": True, "flag_reason": "Exceeds 40% guideline for paint (expected useful life: 5-7 years)", "recoverable_amount": 50.00},
            {"category": "FLR", "description": "Carpet - standard grade", "depreciation_pct": 70.0, "flagged": True, "flag_reason": "Exceeds 60% critical threshold for flooring (expected useful life: 8-10 years)", "recoverable_amount": 200.00},
        ],
    }


@pytest.fixture
def empty_gap_report():
    """A gap report with zero gaps (identical estimates)."""
    return {
        "summary": {"adjuster_rcv": 10000.00, "contractor_rcv": 10000.00, "total_delta": 0.0, "gap_count": 0, "adjuster_line_count": 5, "contractor_line_count": 5},
        "line_item_gaps": [],
        "op_analysis": {"trade_count": 1, "op_warranted": False, "adjuster_op_applied": {"overhead": 0, "profit": 0}, "contractor_op_applied": {"overhead": 0, "profit": 0}, "op_recovery_amount": 0, "trades_detected": ["roofing"]},
        "depreciation_findings": [],
    }


# ===========================================================================
# TASK_J1: Schema Validation Tests
# ===========================================================================

class TestReportSchema:
    def test_report_has_all_required_keys(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        for key in ["report_metadata", "executive_summary", "category_narratives", "financial_summary", "op_narrative", "depreciation_narrative", "recommended_actions"]:
            assert key in report, f"Missing required key: {key}"

    def test_metadata_structure(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        meta = report["report_metadata"]
        assert meta["report_type"] == "supplement_report"
        assert meta["generated_at"] is not None

    def test_executive_summary_structure(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        es = report["executive_summary"]
        for key in ["total_recovery_estimate", "adjuster_rcv", "contractor_rcv", "total_delta", "gap_count", "narrative"]:
            assert key in es
        assert isinstance(es["narrative"], str)
        assert len(es["narrative"]) > 50

    def test_invalid_input_raises(self):
        with pytest.raises(ValueError, match="missing required keys"):
            generate_supplement_report({"summary": {}})


# ===========================================================================
# TASK_J2: Narrative Formatter Tests
# ===========================================================================

class TestNarrativeFormatter:
    def test_category_labels(self):
        assert get_category_label("RFG") == "Roofing"
        assert get_category_label("CNT") == "General Conditions"
        assert get_category_label("UNKNOWN") == "UNKNOWN"

    def test_format_missing_item_detail(self):
        gap = {"gap_type": "missing_item", "description": "Ice & water shield", "contractor_total": 500.00}
        detail = _format_gap_detail(gap)
        assert "Missing item" in detail
        assert "Ice & water shield" in detail
        assert "$500.00" in detail

    def test_format_quantity_delta_detail(self):
        gap = {"gap_type": "quantity_delta", "description": "Shingle roofing", "adjuster_qty": 22, "contractor_qty": 54, "quantity_delta_pct": 145.5, "physical_unit": "SQ"}
        detail = _format_gap_detail(gap)
        assert "Quantity discrepancy" in detail
        assert "22" in detail and "54" in detail

    def test_format_pricing_delta_detail(self):
        gap = {"gap_type": "pricing_delta", "description": "Shingle removal", "adjuster_total": 990.00, "contractor_total": 1100.00, "pricing_delta": 110.00}
        detail = _format_gap_detail(gap)
        assert "Pricing discrepancy" in detail
        assert "$110.00" in detail

    def test_compute_gap_impact_missing(self):
        assert _compute_gap_impact({"gap_type": "missing_item", "contractor_total": 500.0}) == 500.0

    def test_compute_gap_impact_quantity(self):
        assert _compute_gap_impact({"gap_type": "quantity_delta", "contractor_total": 10530.0, "adjuster_total": 4070.0}) == 6460.0

    def test_compute_gap_impact_pricing(self):
        assert _compute_gap_impact({"gap_type": "pricing_delta", "pricing_delta": 110.0}) == 110.0

    def test_category_narratives_grouped(self, mckee_gap_report):
        narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        categories = [n["category"] for n in narratives]
        assert "RFG" in categories
        assert "CNT" in categories

    def test_category_narratives_sorted_by_impact(self, mckee_gap_report):
        narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        impacts = [n["total_impact"] for n in narratives]
        assert impacts == sorted(impacts, reverse=True)

    def test_category_narrative_has_prose(self, mckee_gap_report):
        narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        for n in narratives:
            assert isinstance(n["narrative"], str)
            assert len(n["narrative"]) > 20
            assert n["category_label"] in n["narrative"]

    def test_executive_narrative_format(self, mckee_gap_report):
        narrative = format_executive_narrative(mckee_gap_report["summary"], total_recovery=72000.0, gap_count=17)
        assert "$63,137.79" in narrative
        assert "$123,219.52" in narrative
        assert "17 discrepancies" in narrative

    def test_empty_gaps_empty_narratives(self):
        assert format_category_narratives([]) == []


# ===========================================================================
# TASK_J3: Dollar Summarizer Tests
# ===========================================================================

class TestDollarSummarizer:
    def test_financial_summary_totals(self, mckee_gap_report):
        cat_narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        summary = summarize_financials(cat_narratives, mckee_gap_report["op_analysis"], mckee_gap_report["depreciation_findings"])
        assert summary["op_recovery"] == 12627.56
        assert summary["depreciation_recovery"] == 250.00
        assert summary["line_item_recovery"] > 0
        assert summary["total_recovery"] == pytest.approx(summary["line_item_recovery"] + 12627.56 + 250.00, abs=0.01)

    def test_by_category_percentages(self, mckee_gap_report):
        cat_narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        summary = summarize_financials(cat_narratives, mckee_gap_report["op_analysis"], mckee_gap_report["depreciation_findings"])
        total_pct = sum(c["pct_of_total"] for c in summary["by_category"])
        assert total_pct == pytest.approx(100.0, abs=1.0)

    def test_by_category_sorted_descending(self, mckee_gap_report):
        cat_narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        summary = summarize_financials(cat_narratives, mckee_gap_report["op_analysis"], mckee_gap_report["depreciation_findings"])
        amounts = [c["amount"] for c in summary["by_category"]]
        assert amounts == sorted(amounts, reverse=True)

    def test_op_narrative_warranted(self, mckee_gap_report):
        result = format_op_narrative(mckee_gap_report["op_analysis"])
        assert result["applicable"] is True
        assert result["trade_count"] == 9
        assert result["recovery_amount"] == 12627.56
        assert "warranted" in result["narrative"].lower()

    def test_op_narrative_not_warranted(self):
        op = {"trade_count": 2, "op_warranted": False, "trades_detected": ["roofing", "gutters"], "op_recovery_amount": 0, "adjuster_op_applied": {"overhead": 0, "profit": 0}, "contractor_op_applied": {"overhead": 0, "profit": 0}}
        result = format_op_narrative(op)
        assert result["applicable"] is False
        assert result["recovery_amount"] == 0

    def test_depreciation_narrative_with_findings(self, mckee_gap_report):
        result = format_depreciation_narrative(mckee_gap_report["depreciation_findings"])
        assert result["has_findings"] is True
        assert result["finding_count"] == 2
        assert result["total_recoverable"] == 250.00

    def test_depreciation_narrative_empty(self):
        result = format_depreciation_narrative([])
        assert result["has_findings"] is False
        assert "no items" in result["narrative"].lower()

    def test_recommended_actions_sorted(self, mckee_gap_report):
        cat_narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        fin_summary = summarize_financials(cat_narratives, mckee_gap_report["op_analysis"], mckee_gap_report["depreciation_findings"])
        op_narrative = format_op_narrative(mckee_gap_report["op_analysis"])
        dep_narrative = format_depreciation_narrative(mckee_gap_report["depreciation_findings"])
        actions = build_recommended_actions(cat_narratives, op_narrative, dep_narrative, fin_summary)
        recoveries = [a["expected_recovery"] for a in actions]
        assert recoveries == sorted(recoveries, reverse=True)
        priorities = [a["priority"] for a in actions]
        assert priorities == list(range(1, len(actions) + 1))

    def test_op_is_priority_1_when_warranted(self, mckee_gap_report):
        cat_narratives = format_category_narratives(mckee_gap_report["line_item_gaps"])
        fin_summary = summarize_financials(cat_narratives, mckee_gap_report["op_analysis"], mckee_gap_report["depreciation_findings"])
        op_narrative = format_op_narrative(mckee_gap_report["op_analysis"])
        dep_narrative = format_depreciation_narrative(mckee_gap_report["depreciation_findings"])
        actions = build_recommended_actions(cat_narratives, op_narrative, dep_narrative, fin_summary)
        assert actions[0]["category"] == "O&P"
        assert actions[0]["priority"] == 1


# ===========================================================================
# TASK_J5: Full Integration — generate_supplement_report
# ===========================================================================

class TestGenerateSupplementReport:
    def test_full_mckee_report(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        for key in ["report_metadata", "executive_summary", "category_narratives", "financial_summary", "op_narrative", "depreciation_narrative", "recommended_actions"]:
            assert key in report

    def test_total_recovery_matches_mckee(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        fs = report["financial_summary"]
        assert fs["op_recovery"] == 12627.56
        assert fs["depreciation_recovery"] == 250.00
        expected_total = fs["line_item_recovery"] + 12627.56 + 250.00
        assert fs["total_recovery"] == pytest.approx(expected_total, abs=0.01)

    def test_gap_count_matches(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        assert report["executive_summary"]["gap_count"] == 17

    def test_delta_matches(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        es = report["executive_summary"]
        assert es["adjuster_rcv"] == 63137.79
        assert es["contractor_rcv"] == 123219.52
        assert es["total_delta"] == pytest.approx(60081.73, abs=0.01)

    def test_categories_present(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        cat_codes = [c["category"] for c in report["category_narratives"]]
        assert "RFG" in cat_codes
        assert "CNT" in cat_codes

    def test_op_warranted_in_report(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        op = report["op_narrative"]
        assert op["applicable"] is True
        assert op["trade_count"] == 9
        assert op["recovery_amount"] == 12627.56

    def test_depreciation_in_report(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        dep = report["depreciation_narrative"]
        assert dep["has_findings"] is True
        assert dep["finding_count"] == 2

    def test_recommended_actions_present(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report)
        actions = report["recommended_actions"]
        assert len(actions) > 0
        assert actions[0]["category"] == "O&P"

    def test_empty_gap_report_valid(self, empty_gap_report):
        report = generate_supplement_report(empty_gap_report)
        fs = report["financial_summary"]
        assert fs["line_item_recovery"] == 0
        assert fs["op_recovery"] == 0
        assert fs["total_recovery"] == 0
        assert report["executive_summary"]["gap_count"] == 0
        assert len(report["category_narratives"]) == 0
        assert report["op_narrative"]["applicable"] is False

    def test_report_id_passthrough(self, mckee_gap_report):
        report = generate_supplement_report(mckee_gap_report, report_id="RPT-2024-001")
        assert report["report_metadata"]["source_gap_report_id"] == "RPT-2024-001"

    def test_total_recovery_exceeds_15k(self, mckee_gap_report):
        """McKee case total recovery should be substantial (> $15K minimum from O&P alone)."""
        report = generate_supplement_report(mckee_gap_report)
        total = report["financial_summary"]["total_recovery"]
        assert total > 15000, f"Total recovery ${total:,.2f} seems too low"
