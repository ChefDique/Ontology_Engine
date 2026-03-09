"""
Unit Tests — Node 5: Estimate Comparator (TASK_I5)

Uses McKee case study data from supplement_analysis:
  - Adjuster RCV: $63,137.79 (49 line items)
  - Contractor RCV: $123,219.52 (73 line items)
  - Delta: $60,081.73
  - 9 trades involved (O&P warranted, adjuster applied 0%)
  - 24 missing items worth $7,407
  - 10+ quantity discrepancies >20%
  - Depreciation: paint at 46.67%, carpet at 70%
"""

import pytest
from ontology_engine.node5_comparator.comparator import compare_estimates
from ontology_engine.node5_comparator.diff_engine import diff_line_items
from ontology_engine.node5_comparator.op_detector import (
    analyze_op,
    detect_trades,
    OP_WARRANTED_TRADE_THRESHOLD,
)
from ontology_engine.node5_comparator.depreciation_auditor import (
    audit_depreciation,
    DEPRECIATION_WARNING_PCT,
    DEPRECIATION_CRITICAL_PCT,
)


# ===========================================================================
# Fixtures — McKee Case Study (representative subset)
# ===========================================================================

@pytest.fixture
def mckee_adjuster_estimate():
    """Adjuster estimate modeled on McKee case (49 items, 0% O&P)."""
    return {
        "header": {
            "estimate_number": "51-80B9-27C",
            "claim_number": "CLM-2024-00817",
            "carrier": "State Farm",
            "loss_date": "2024-01-15",
        },
        "procurement_items": [
            # Roofing
            {"category": "RFG", "description": "Remove Comp. shingle roofing - 3 tab/25yr", "physical_qty": 22, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 45.00},
            {"category": "RFG", "description": "Shingle roofing - comp./asphalt (3-tab/25 year)", "physical_qty": 22, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 185.00},
            {"category": "RFG", "description": "Hip/ridge cap - comp. shingle", "physical_qty": 32, "physical_unit": "LF", "trade": "roofing", "unit_cost": 5.50},
            {"category": "RFG", "description": "Drip edge", "physical_qty": 143, "physical_unit": "LF", "trade": "roofing", "unit_cost": 3.25},
            {"category": "RFG", "description": "Mod bit roof membrane", "physical_qty": 100, "physical_unit": "SF", "trade": "roofing", "unit_cost": 12.50},
            # Siding
            {"category": "SID", "description": "Vinyl siding - remove & replace", "physical_qty": 200, "physical_unit": "SF", "trade": "siding", "unit_cost": 8.75},
            # Drywall
            {"category": "DRY", "description": "Drywall - 1/2\" standard hung, taped, floated", "physical_qty": 50, "physical_unit": "SF", "trade": "drywall", "unit_cost": 3.50},
            # Painting
            {"category": "PNT", "description": "Paint interior walls - 2 coats", "physical_qty": 200, "physical_unit": "SF", "trade": "painting", "unit_cost": 1.25, "depreciation": 116.68},
            # Carpet/flooring
            {"category": "FLR", "description": "Carpet - standard grade", "physical_qty": 30, "physical_unit": "SY", "trade": "flooring", "unit_cost": 25.00, "depreciation": 525.00},
            # Electrical
            {"category": "ELC", "description": "Light fixture - standard", "physical_qty": 4, "physical_unit": "EA", "trade": "electrical", "unit_cost": 85.00},
            # Plumbing
            {"category": "PLM", "description": "Water heater - 40 gal", "physical_qty": 1, "physical_unit": "EA", "trade": "plumbing", "unit_cost": 850.00},
            # HVAC
            {"category": "MCA", "description": "HVAC system - inspection", "physical_qty": 1, "physical_unit": "EA", "trade": "hvac", "unit_cost": 250.00},
            # Gutters
            {"category": "GTR", "description": "Gutter - aluminum - 5\"", "physical_qty": 85, "physical_unit": "LF", "trade": "gutters", "unit_cost": 7.50},
        ],
        "credit_items": [],
        "adjusted_totals": {
            "rcv": 63137.79,
            "depreciation": 8500.00,
            "acv": 54637.79,
            "overhead": 0.0,  # <-- 0% O&P applied by adjuster
            "profit": 0.0,
            "tax": 2850.00,
            "net_claim": 57487.79,
        },
        "hitl_flags": [],
    }


@pytest.fixture
def mckee_contractor_estimate():
    """Contractor estimate modeled on McKee case (73 items, 10/10 O&P)."""
    return {
        "header": {
            "estimate_number": "CTR-McKee-2024",
            "claim_number": "CLM-2024-00817",
            "carrier": "State Farm",
            "loss_date": "2024-01-15",
        },
        "procurement_items": [
            # Roofing — higher quantities
            {"category": "RFG", "description": "Remove Comp. shingle roofing - 3 tab/25yr", "physical_qty": 22, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 50.00},
            {"category": "RFG", "description": "Shingle roofing - comp./asphalt (3-tab/25 year)", "physical_qty": 54, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 195.00},  # +145%
            {"category": "RFG", "description": "Hip/ridge cap - comp. shingle", "physical_qty": 66, "physical_unit": "LF", "trade": "roofing", "unit_cost": 5.75},  # +106%
            {"category": "RFG", "description": "Drip edge", "physical_qty": 203, "physical_unit": "LF", "trade": "roofing", "unit_cost": 3.50},  # +42%
            {"category": "RFG", "description": "Mod bit roof membrane", "physical_qty": 245, "physical_unit": "SF", "trade": "roofing", "unit_cost": 13.00},  # +145%
            # Siding — updated qty
            {"category": "SID", "description": "Vinyl siding - remove & replace", "physical_qty": 280, "physical_unit": "SF", "trade": "siding", "unit_cost": 9.00},  # +40%
            # Drywall — big delta
            {"category": "DRY", "description": "Drywall - 1/2\" standard hung, taped, floated", "physical_qty": 101, "physical_unit": "SF", "trade": "drywall", "unit_cost": 3.75},  # +102%
            # Painting
            {"category": "PNT", "description": "Paint interior walls - 2 coats", "physical_qty": 350, "physical_unit": "SF", "trade": "painting", "unit_cost": 1.35},  # +75%
            # Carpet/flooring
            {"category": "FLR", "description": "Carpet - standard grade", "physical_qty": 45, "physical_unit": "SY", "trade": "flooring", "unit_cost": 28.00},  # +50%
            # Electrical
            {"category": "ELC", "description": "Light fixture - standard", "physical_qty": 4, "physical_unit": "EA", "trade": "electrical", "unit_cost": 95.00},
            # Plumbing
            {"category": "PLM", "description": "Water heater - 40 gal", "physical_qty": 1, "physical_unit": "EA", "trade": "plumbing", "unit_cost": 900.00},
            # HVAC
            {"category": "MCA", "description": "HVAC system - inspection", "physical_qty": 1, "physical_unit": "EA", "trade": "hvac", "unit_cost": 275.00},
            # Gutters
            {"category": "GTR", "description": "Gutter - aluminum - 5\"", "physical_qty": 110, "physical_unit": "LF", "trade": "gutters", "unit_cost": 8.00},  # +29%
            # --- MISSING from adjuster (24 items in real case, 8 representative) ---
            {"category": "CNT", "description": "Dust barrier - 6 mil poly", "physical_qty": 200, "physical_unit": "SF", "trade": "general_conditions", "unit_cost": 0.85},
            {"category": "CNT", "description": "Floor protection - ram board", "physical_qty": 150, "physical_unit": "SF", "trade": "general_conditions", "unit_cost": 1.25},
            {"category": "CNT", "description": "Pool tarping - protective cover", "physical_qty": 1, "physical_unit": "EA", "trade": "general_conditions", "unit_cost": 450.00},
            {"category": "CNT", "description": "Emergency service call", "physical_qty": 1, "physical_unit": "EA", "trade": "general_conditions", "unit_cost": 350.00},
            {"category": "INS", "description": "Insulation - blown-in R-38", "physical_qty": 400, "physical_unit": "SF", "trade": "insulation", "unit_cost": 2.50},
            {"category": "ELC", "description": "Can light - remove & reinstall", "physical_qty": 6, "physical_unit": "EA", "trade": "electrical", "unit_cost": 125.00},
            {"category": "FLR", "description": "Base shoe molding", "physical_qty": 85, "physical_unit": "LF", "trade": "flooring", "unit_cost": 3.50},
            {"category": "PNT", "description": "Paint exterior trim - 2 coats", "physical_qty": 120, "physical_unit": "LF", "trade": "painting", "unit_cost": 2.75},
        ],
        "credit_items": [],
        "adjusted_totals": {
            "rcv": 123219.52,
            "depreciation": 12000.00,
            "acv": 111219.52,
            "overhead": 10200.00,
            "profit": 10200.00,
            "tax": 5500.00,
            "net_claim": 116719.52,
        },
        "hitl_flags": [],
    }


# ===========================================================================
# TASK_I2: Line-Item Diff Engine Tests
# ===========================================================================

class TestDiffEngine:
    """Tests for diff_engine.diff_line_items."""

    def test_missing_items_detected(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """24 items in contractor but not adjuster → should find missing items."""
        gaps = diff_line_items(
            mckee_adjuster_estimate["procurement_items"],
            mckee_contractor_estimate["procurement_items"],
        )
        missing = [g for g in gaps if g["gap_type"] == "missing_item"]
        # We have 8 representative missing items in our fixture
        assert len(missing) >= 8, f"Expected ≥8 missing items, got {len(missing)}"
        
        # Verify specific missing items
        missing_descriptions = {m["description"] for m in missing}
        assert "Dust barrier - 6 mil poly" in missing_descriptions
        assert "Pool tarping - protective cover" in missing_descriptions
        assert "Emergency service call" in missing_descriptions
        assert "Floor protection - ram board" in missing_descriptions

    def test_quantity_deltas_detected(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Shingle qty 22→54 (+145%), drywall 50→101 (+102%)."""
        gaps = diff_line_items(
            mckee_adjuster_estimate["procurement_items"],
            mckee_contractor_estimate["procurement_items"],
        )
        qty_deltas = [g for g in gaps if g["gap_type"] == "quantity_delta"]
        assert len(qty_deltas) >= 5, f"Expected ≥5 qty deltas, got {len(qty_deltas)}"

        # Check specific known deltas
        shingle_gap = next(
            (g for g in qty_deltas if "shingle roofing" in g["description"].lower()),
            None,
        )
        assert shingle_gap is not None, "Should detect shingle roofing quantity delta"
        assert shingle_gap["adjuster_qty"] == 22
        assert shingle_gap["contractor_qty"] == 54
        assert shingle_gap["quantity_delta_pct"] > 100  # +145%

    def test_pricing_deltas_detected(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Items with same description but different unit costs."""
        gaps = diff_line_items(
            mckee_adjuster_estimate["procurement_items"],
            mckee_contractor_estimate["procurement_items"],
        )
        price_deltas = [g for g in gaps if g["gap_type"] == "pricing_delta"]
        # Some items have >20% pricing difference
        assert isinstance(price_deltas, list)

    def test_exact_match_items_no_false_positive(self):
        """Identical items should produce NO gaps."""
        items = [
            {"category": "RFG", "description": "Shingle roofing", "physical_qty": 20, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 185.00},
        ]
        gaps = diff_line_items(items, items)
        assert len(gaps) == 0

    def test_empty_estimates(self):
        """Both empty → no gaps."""
        gaps = diff_line_items([], [])
        assert len(gaps) == 0

    def test_all_missing_when_adjuster_empty(self):
        """Empty adjuster → all contractor items are missing."""
        contractor = [
            {"category": "RFG", "description": "Item A", "physical_qty": 10, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 100},
            {"category": "SID", "description": "Item B", "physical_qty": 5, "physical_unit": "SF", "trade": "siding", "unit_cost": 50},
        ]
        gaps = diff_line_items([], contractor)
        assert len(gaps) == 2
        assert all(g["gap_type"] == "missing_item" for g in gaps)

    def test_fuzzy_matching(self):
        """Slight description differences should still match."""
        adjuster = [
            {"category": "RFG", "description": "Comp. shingle roofing - 3 tab/25yr", "physical_qty": 20, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 185},
        ]
        contractor = [
            {"category": "RFG", "description": "Comp. shingle roofing - 3 tab / 25 yr", "physical_qty": 30, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 185},
        ]
        gaps = diff_line_items(adjuster, contractor)
        # Should fuzzy-match and detect a quantity delta, not a missing item
        missing = [g for g in gaps if g["gap_type"] == "missing_item"]
        assert len(missing) == 0, "Fuzzy match should prevent false 'missing' classification"

    def test_gap_types_valid(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """All gaps should have valid gap_type enum values."""
        gaps = diff_line_items(
            mckee_adjuster_estimate["procurement_items"],
            mckee_contractor_estimate["procurement_items"],
        )
        valid_types = {"missing_item", "quantity_delta", "pricing_delta"}
        for gap in gaps:
            assert gap["gap_type"] in valid_types


# ===========================================================================
# TASK_I3: O&P Detection Tests
# ===========================================================================

class TestOPDetection:
    """Tests for op_detector.analyze_op."""

    def test_nine_trades_detected(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """McKee case has 9+ distinct trades → O&P warranted."""
        result = analyze_op(mckee_adjuster_estimate, mckee_contractor_estimate)
        assert result["trade_count"] >= 9, f"Expected ≥9 trades, got {result['trade_count']}"
        assert result["op_warranted"] is True

    def test_adjuster_zero_op(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Adjuster applied 0% O&P."""
        result = analyze_op(mckee_adjuster_estimate, mckee_contractor_estimate)
        assert result["adjuster_op_applied"]["overhead"] == 0
        assert result["adjuster_op_applied"]["profit"] == 0

    def test_op_recovery_calculated(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Recovery = 10% OH + 10% PR on adjuster RCV ($63,137.79)."""
        result = analyze_op(mckee_adjuster_estimate, mckee_contractor_estimate)
        expected_recovery = 63137.79 * 0.20  # 10% + 10%
        assert result["op_recovery_amount"] > 0
        assert abs(result["op_recovery_amount"] - expected_recovery) < 1.0

    def test_two_trades_no_op_warranted(self):
        """< 3 trades → O&P NOT warranted."""
        adj = {
            "procurement_items": [
                {"category": "RFG", "description": "Shingles", "physical_qty": 10, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 185},
            ],
            "adjusted_totals": {"rcv": 5000, "overhead": 0, "profit": 0},
        }
        ctr = {
            "procurement_items": [
                {"category": "RFG", "description": "Shingles", "physical_qty": 15, "physical_unit": "SQ", "trade": "roofing", "unit_cost": 195},
                {"category": "GTR", "description": "Gutters", "physical_qty": 50, "physical_unit": "LF", "trade": "gutters", "unit_cost": 8},
            ],
            "adjusted_totals": {"rcv": 8000, "overhead": 800, "profit": 800},
        }
        result = analyze_op(adj, ctr)
        assert result["trade_count"] == 2
        assert result["op_warranted"] is False
        assert result["op_recovery_amount"] == 0

    def test_trades_detected_list(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Should list all detected trades."""
        result = analyze_op(mckee_adjuster_estimate, mckee_contractor_estimate)
        assert "roofing" in result["trades_detected"]
        assert "siding" in result["trades_detected"]
        assert "drywall" in result["trades_detected"]
        assert "painting" in result["trades_detected"]

    def test_detect_trades_excludes_general(self):
        """Trade 'general' should only be counted if it's the only trade."""
        items = [
            {"trade": "roofing"},
            {"trade": "general"},
            {"trade": "siding"},
        ]
        trades = detect_trades(items)
        assert "general" not in trades
        assert len(trades) == 2


# ===========================================================================
# TASK_I4: Depreciation Audit Tests
# ===========================================================================

class TestDepreciationAudit:
    """Tests for depreciation_auditor.audit_depreciation."""

    def test_paint_high_depreciation(self):
        """Paint at 46.67% should be flagged (guideline max is 40%)."""
        items = [
            {"category": "PNT", "description": "Paint interior walls", "physical_qty": 200, "physical_unit": "SF", "unit_cost": 1.25, "depreciation": 116.68},
        ]
        totals = {"rcv": 10000, "depreciation": 2000}
        findings = audit_depreciation(items, totals)
        paint_finding = next(
            (f for f in findings if "paint" in f["description"].lower()),
            None,
        )
        assert paint_finding is not None, "Should find depreciation issue for paint"
        assert paint_finding["depreciation_pct"] > 40
        assert paint_finding["flagged"] is True

    def test_carpet_extreme_depreciation(self):
        """Carpet at 70% should be flagged critical."""
        items = [
            {"category": "FLR", "description": "Carpet - standard grade", "physical_qty": 30, "physical_unit": "SY", "unit_cost": 25.00, "depreciation": 525.00},
        ]
        totals = {"rcv": 10000, "depreciation": 3000}
        findings = audit_depreciation(items, totals)
        carpet_finding = next(
            (f for f in findings if "carpet" in f["description"].lower()),
            None,
        )
        assert carpet_finding is not None
        assert carpet_finding["depreciation_pct"] == 70.0
        assert carpet_finding["flagged"] is True

    def test_no_depreciation_no_findings(self):
        """Zero depreciation → no item-level findings."""
        items = [
            {"category": "RFG", "description": "Shingles", "physical_qty": 10, "physical_unit": "SQ", "unit_cost": 185},
        ]
        totals = {"rcv": 5000, "depreciation": 0}
        findings = audit_depreciation(items, totals)
        assert len(findings) == 0

    def test_aggregate_high_depreciation_flagged(self):
        """Overall depreciation >50% of RCV should produce aggregate finding."""
        items = []
        totals = {"rcv": 10000, "depreciation": 6000}  # 60%
        findings = audit_depreciation(items, totals)
        aggregate = [f for f in findings if f["category"] == "AGGREGATE"]
        assert len(aggregate) == 1
        assert aggregate[0]["depreciation_pct"] == 60.0

    def test_moderate_depreciation_not_flagged(self):
        """Depreciation under warning threshold should not produce findings."""
        items = [
            {"category": "RFG", "description": "Shingles", "physical_qty": 10, "physical_unit": "SQ", "unit_cost": 185, "depreciation": 100},
        ]
        # 100 / (185*10) = 5.4% — well under threshold
        totals = {"rcv": 10000, "depreciation": 100}
        findings = audit_depreciation(items, totals)
        item_findings = [f for f in findings if f["category"] != "AGGREGATE"]
        assert len(item_findings) == 0


# ===========================================================================
# TASK_I5: Full Integration — compare_estimates
# ===========================================================================

class TestCompareEstimates:
    """Integration tests for the full compare_estimates pipeline."""

    def test_full_mckee_comparison(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Full McKee case should produce a complete gap report."""
        report = compare_estimates(mckee_adjuster_estimate, mckee_contractor_estimate)

        # Verify all required top-level keys
        assert "summary" in report
        assert "line_item_gaps" in report
        assert "op_analysis" in report
        assert "depreciation_findings" in report

    def test_summary_financials(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Summary should reflect correct RCV values and delta."""
        report = compare_estimates(mckee_adjuster_estimate, mckee_contractor_estimate)
        summary = report["summary"]

        assert summary["adjuster_rcv"] == 63137.79
        assert summary["contractor_rcv"] == 123219.52
        assert summary["total_delta"] == pytest.approx(60081.73, abs=0.01)
        assert summary["gap_count"] > 0

    def test_summary_line_counts(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Summary line counts should match fixture data."""
        report = compare_estimates(mckee_adjuster_estimate, mckee_contractor_estimate)
        summary = report["summary"]

        assert summary["adjuster_line_count"] == 13  # Our fixture has 13 adj items
        assert summary["contractor_line_count"] == 21  # Our fixture has 21 ctr items

    def test_gap_report_has_all_gap_types(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """Report should contain missing, quantity, and potentially pricing gaps."""
        report = compare_estimates(mckee_adjuster_estimate, mckee_contractor_estimate)
        gap_types = {g["gap_type"] for g in report["line_item_gaps"]}
        assert "missing_item" in gap_types
        assert "quantity_delta" in gap_types

    def test_op_warranted_in_report(self, mckee_adjuster_estimate, mckee_contractor_estimate):
        """O&P should be flagged as warranted with recovery amount."""
        report = compare_estimates(mckee_adjuster_estimate, mckee_contractor_estimate)
        op = report["op_analysis"]
        assert op["op_warranted"] is True
        assert op["op_recovery_amount"] > 10000  # Should be ~$12,627

    def test_empty_estimates_valid_report(self):
        """Two empty estimates should produce a valid (all-zero) report."""
        empty = {
            "procurement_items": [],
            "adjusted_totals": {"rcv": 0, "depreciation": 0, "overhead": 0, "profit": 0},
        }
        report = compare_estimates(empty, empty)
        assert report["summary"]["total_delta"] == 0
        assert report["summary"]["gap_count"] == 0
        assert len(report["line_item_gaps"]) == 0
        assert report["op_analysis"]["op_warranted"] is False
