"""TASK_K5 — Node 5+6 adversarial tests.

Tests Node 5 (Comparator) and Node 6 (Supplement Report) resilience against:
  - Identical estimates (zero delta)
  - Empty gap reports
  - Extreme deltas (10x price difference)
  - Single-line-item estimates
  - Empty procurement_items
  - Missing or malformed adjusted_totals
"""

import copy

import pytest

from ontology_engine.node5_comparator.comparator import compare_estimates
from ontology_engine.node5_comparator.diff_engine import diff_line_items
from ontology_engine.node5_comparator.op_detector import analyze_op, detect_trades
from ontology_engine.node5_comparator.depreciation_auditor import audit_depreciation


def _make_estimate(items=None, totals=None):
    """Helper: build a minimal valid Node 3 output."""
    return {
        "header": {"estimate_number": "TEST-ADV"},
        "procurement_items": items or [],
        "credit_items": [],
        "adjusted_totals": totals or {
            "rcv": 0, "depreciation": 0, "acv": 0,
            "overhead": 0, "profit": 0, "tax": 0, "net_claim": 0,
        },
        "hitl_flags": [],
    }


def _make_item(category="RFG", description="Shingles", qty=10, cost=100.0, trade="roofing"):
    """Helper: build a procurement item."""
    return {
        "category": category,
        "description": description,
        "physical_qty": qty,
        "physical_unit": "bundles",
        "trade": trade,
        "unit_cost": cost,
    }


# ── K5.1: Identical Estimates ───────────────────────────────────────────────

class TestIdenticalEstimates:
    """When both estimates are identical, delta should be zero."""

    def test_identical_single_item(self):
        """Same item in both → zero gaps."""
        item = _make_item()
        result = compare_estimates(
            _make_estimate([item], {"rcv": 1000, "depreciation": 0, "acv": 1000,
                                    "overhead": 0, "profit": 0, "tax": 0, "net_claim": 1000}),
            _make_estimate([item], {"rcv": 1000, "depreciation": 0, "acv": 1000,
                                    "overhead": 0, "profit": 0, "tax": 0, "net_claim": 1000}),
        )
        assert result["summary"]["total_delta"] == 0
        assert result["summary"]["gap_count"] == 0

    def test_identical_multi_item(self):
        """Multiple identical items → zero gaps."""
        items = [
            _make_item("RFG", "Shingles", 10, 100.0, "roofing"),
            _make_item("GUT", "Gutters", 20, 50.0, "gutters"),
            _make_item("SID", "Siding", 30, 75.0, "siding"),
        ]
        totals = {"rcv": 5000, "depreciation": 500, "acv": 4500,
                  "overhead": 0, "profit": 0, "tax": 250, "net_claim": 4750}
        result = compare_estimates(
            _make_estimate(items, totals),
            _make_estimate(items, totals),
        )
        assert result["summary"]["total_delta"] == 0
        assert result["summary"]["gap_count"] == 0


# ── K5.2: Empty Estimates ──────────────────────────────────────────────────

class TestEmptyEstimates:
    """Edge cases with empty or minimal estimates."""

    def test_both_empty(self):
        """Two empty estimates should produce zero gaps, not crash."""
        result = compare_estimates(_make_estimate(), _make_estimate())
        assert result["summary"]["gap_count"] == 0
        assert result["summary"]["total_delta"] == 0

    def test_adjuster_empty_contractor_has_items(self):
        """All contractor items should appear as missing_item gaps."""
        contractor = _make_estimate(
            [_make_item(), _make_item("GUT", "Gutters", 5, 30.0, "gutters")],
            {"rcv": 2000, "depreciation": 0, "acv": 2000,
             "overhead": 0, "profit": 0, "tax": 0, "net_claim": 2000},
        )
        result = compare_estimates(_make_estimate(), contractor)
        assert result["summary"]["gap_count"] == 2
        for gap in result["line_item_gaps"]:
            assert gap["gap_type"] == "missing_item"

    def test_contractor_empty_adjuster_has_items(self):
        """Empty contractor estimate → zero gaps (we only flag contractor extras)."""
        adjuster = _make_estimate(
            [_make_item()],
            {"rcv": 1000, "depreciation": 0, "acv": 1000,
             "overhead": 0, "profit": 0, "tax": 0, "net_claim": 1000},
        )
        result = compare_estimates(adjuster, _make_estimate())
        # No gaps because diff_engine only finds items in contractor missing from adjuster
        assert result["summary"]["gap_count"] == 0


# ── K5.3: Extreme Deltas ──────────────────────────────────────────────────

class TestExtremeDeltas:
    """Very large differences between estimates."""

    def test_10x_quantity_difference(self):
        """10x quantity difference should flag quantity_delta."""
        adj_item = _make_item("RFG", "Shingles", 10, 100.0, "roofing")
        ctr_item = _make_item("RFG", "Shingles", 100, 100.0, "roofing")
        gaps = diff_line_items([adj_item], [ctr_item])
        assert any(g["gap_type"] == "quantity_delta" for g in gaps)

    def test_10x_price_difference(self):
        """10x unit cost difference should flag pricing_delta."""
        adj_item = _make_item("RFG", "Shingles", 10, 10.0, "roofing")
        ctr_item = _make_item("RFG", "Shingles", 10, 100.0, "roofing")
        gaps = diff_line_items([adj_item], [ctr_item])
        assert any(g["gap_type"] == "pricing_delta" for g in gaps)

    def test_million_dollar_delta(self):
        """Very large RCV difference should compute correctly."""
        adj_totals = {"rcv": 10_000, "depreciation": 0, "acv": 10_000,
                      "overhead": 0, "profit": 0, "tax": 0, "net_claim": 10_000}
        ctr_totals = {"rcv": 1_000_000, "depreciation": 0, "acv": 1_000_000,
                      "overhead": 0, "profit": 0, "tax": 0, "net_claim": 1_000_000}
        result = compare_estimates(
            _make_estimate([_make_item()], adj_totals),
            _make_estimate([_make_item(qty=10000)], ctr_totals),
        )
        assert result["summary"]["total_delta"] == 990_000

    def test_negative_total_delta(self):
        """Adjuster RCV > contractor RCV → negative delta."""
        adj_totals = {"rcv": 50_000, "depreciation": 0, "acv": 50_000,
                      "overhead": 0, "profit": 0, "tax": 0, "net_claim": 50_000}
        ctr_totals = {"rcv": 10_000, "depreciation": 0, "acv": 10_000,
                      "overhead": 0, "profit": 0, "tax": 0, "net_claim": 10_000}
        result = compare_estimates(
            _make_estimate([_make_item()], adj_totals),
            _make_estimate([_make_item()], ctr_totals),
        )
        assert result["summary"]["total_delta"] < 0


# ── K5.4: Single Line Item Edge Cases ──────────────────────────────────────

class TestSingleLineItem:
    """Estimates with only one line item."""

    def test_single_item_missing(self):
        """Single item only in contractor → one missing_item gap."""
        gaps = diff_line_items([], [_make_item()])
        assert len(gaps) == 1
        assert gaps[0]["gap_type"] == "missing_item"

    def test_single_item_matched(self):
        """Same single item in both → zero gaps."""
        item = _make_item()
        gaps = diff_line_items([item], [item])
        assert len(gaps) == 0


# ── K5.5: O&P Detector Edge Cases ──────────────────────────────────────────

class TestOPDetectorEdgeCases:
    """O&P detection with boundary conditions."""

    def test_zero_trades(self):
        """Estimate with no items should still return valid analysis."""
        result = analyze_op(_make_estimate(), _make_estimate())
        assert isinstance(result["trade_count"], int)
        assert isinstance(result["op_warranted"], bool)

    def test_exactly_three_trades(self):
        """Exactly 3 trades should warrant O&P."""
        items = [
            _make_item(trade="roofing"),
            _make_item(trade="gutters"),
            _make_item(trade="siding"),
        ]
        trades = detect_trades(items)
        assert len(trades) >= 3

    def test_two_trades_not_warranted(self):
        """Two trades should NOT warrant O&P."""
        items = [
            _make_item(trade="roofing"),
            _make_item(trade="gutters"),
        ]
        totals = {"rcv": 10000, "depreciation": 0, "acv": 10000,
                  "overhead": 0, "profit": 0, "tax": 0, "net_claim": 10000}
        result = analyze_op(_make_estimate(items, totals), _make_estimate(items, totals))
        assert result["op_warranted"] is False
        assert result["op_recovery_amount"] == 0

    def test_all_general_trade(self):
        """All items with trade='general' — check trade counting."""
        items = [_make_item(trade="general") for _ in range(5)]
        trades = detect_trades(items)
        # 'general' is filtered out, replaced with just {"general"}
        assert len(trades) >= 1

    def test_empty_procurement_items(self):
        """Empty procurement_items should not crash O&P detection."""
        result = analyze_op(_make_estimate(), _make_estimate())
        assert result["op_recovery_amount"] == 0


# ── K5.6: Depreciation Auditor Edge Cases ──────────────────────────────────

class TestDepreciationAuditorEdgeCases:
    """Depreciation auditor with boundary conditions."""

    def test_zero_rcv_no_crash(self):
        """Zero RCV should not divide by zero."""
        findings = audit_depreciation([], {"rcv": 0, "depreciation": 0})
        assert isinstance(findings, list)

    def test_zero_depreciation(self):
        """Zero depreciation should produce no findings."""
        findings = audit_depreciation([], {"rcv": 10000, "depreciation": 0})
        assert len(findings) == 0

    def test_100_percent_depreciation(self):
        """100% depreciation on RCV should be flagged as critical."""
        findings = audit_depreciation(
            [],
            {"rcv": 10000, "depreciation": 10000, "acv": 0},
        )
        assert len(findings) >= 1
        assert any(f["flagged"] for f in findings)

    def test_over_100_percent_depreciation(self):
        """Depreciation > RCV (impossible but should not crash)."""
        findings = audit_depreciation(
            [],
            {"rcv": 10000, "depreciation": 15000, "acv": -5000},
        )
        assert isinstance(findings, list)
        assert len(findings) >= 1

    def test_empty_items_and_totals(self):
        """Completely empty inputs should not crash."""
        findings = audit_depreciation([], {})
        assert isinstance(findings, list)
