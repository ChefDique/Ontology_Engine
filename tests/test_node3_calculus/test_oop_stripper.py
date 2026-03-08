"""Tests for O&P Stripper — TASK_B4."""

import pytest
from ontology_engine.node3_calculus.oop_stripper import strip_overhead_and_profit


class TestStripOverheadAndProfit:
    """Test O&P stripping with Decimal precision."""

    SAMPLE_TOTALS = {
        "rcv": 10000.00,
        "depreciation": 2000.00,
        "acv": 8000.00,
        "overhead": 1000.00,
        "profit": 1000.00,
        "tax": 500.00,
        "net_claim": 8500.00,
    }

    def test_strips_overhead_and_profit(self):
        result = strip_overhead_and_profit(self.SAMPLE_TOTALS, [])
        adj = result["adjusted_totals"]
        assert adj["overhead"] == 0.0
        assert adj["profit"] == 0.0

    def test_adjusted_rcv(self):
        result = strip_overhead_and_profit(self.SAMPLE_TOTALS, [])
        adj = result["adjusted_totals"]
        # 10000 - 1000 - 1000 = 8000
        assert adj["rcv"] == 8000.00

    def test_adjusted_acv(self):
        result = strip_overhead_and_profit(self.SAMPLE_TOTALS, [])
        adj = result["adjusted_totals"]
        # 8000 - 2000 = 6000
        assert adj["acv"] == 6000.00

    def test_tax_recalculated(self):
        result = strip_overhead_and_profit(self.SAMPLE_TOTALS, [])
        adj = result["adjusted_totals"]
        # Tax rate = 500 / 10000 = 0.05
        # Adjusted tax = 8000 × 0.05 = 400
        assert adj["tax"] == 400.00

    def test_stripped_amounts_returned(self):
        result = strip_overhead_and_profit(self.SAMPLE_TOTALS, [])
        assert result["stripped_overhead"] == 1000.00
        assert result["stripped_profit"] == 1000.00

    def test_note_present(self):
        result = strip_overhead_and_profit(self.SAMPLE_TOTALS, [])
        assert result["note"] == "O&P stripped"

    def test_zero_overhead_profit(self):
        totals = {**self.SAMPLE_TOTALS, "overhead": 0, "profit": 0}
        result = strip_overhead_and_profit(totals, [])
        adj = result["adjusted_totals"]
        assert adj["rcv"] == 10000.00
        assert result["stripped_overhead"] == 0.0

    def test_no_tax(self):
        totals = {**self.SAMPLE_TOTALS, "tax": 0}
        result = strip_overhead_and_profit(totals, [])
        adj = result["adjusted_totals"]
        assert adj["tax"] == 0.0

    def test_decimal_precision(self):
        """Ensure no floating point errors in currency calculations."""
        totals = {
            "rcv": 7046.72,
            "depreciation": 1200.00,
            "acv": 5846.72,
            "overhead": 704.67,
            "profit": 704.67,
            "tax": 352.34,
            "net_claim": 6903.39,
        }
        result = strip_overhead_and_profit(totals, [])
        adj = result["adjusted_totals"]
        # RCV = 7046.72 - 704.67 - 704.67 = 5637.38
        assert adj["rcv"] == 5637.38
        # All values should be clean 2-decimal floats
        for key, val in adj.items():
            assert round(val, 2) == val, f"{key} has precision error: {val}"
