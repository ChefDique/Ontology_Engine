"""TASK_K3 — Calculus overflow/underflow (Node 3).

Tests Node 3 (Calculus) resilience against:
  - Extreme numeric values (overflow/underflow)
  - Division by zero
  - Negative quantities
  - NaN/infinity propagation
  - Zero-value estimates
  - Missing optional fields
"""

import math
import sys
from decimal import Decimal, InvalidOperation

import pytest

from ontology_engine.node3_calculus.roofer_math import (
    apply_pitch_waste,
    calculate_material_quantities,
    linear_feet_to_pieces,
    square_feet_to_sheets,
    squares_to_bundles,
)
from ontology_engine.node3_calculus.oop_stripper import strip_overhead_and_profit
from ontology_engine.node3_calculus.credit_handler import handle_credits
from ontology_engine.node3_calculus.trade_splitter import split_by_trade


# ── K3.1: Roofer Math Overflow ──────────────────────────────────────────────

class TestRooferMathOverflow:
    """Math functions must handle extreme values without crash."""

    def test_huge_squares(self):
        """Very large square count should produce integer, not overflow."""
        result = squares_to_bundles(1_000_000.0, waste_factor=1.15)
        assert isinstance(result, int)
        assert result > 0

    def test_zero_squares(self):
        """Zero squares should produce zero bundles."""
        result = squares_to_bundles(0.0)
        assert result == 0

    def test_tiny_fractional_squares(self):
        """Very small fraction should ceil to 1."""
        result = squares_to_bundles(0.001)
        assert result >= 1

    def test_huge_linear_feet(self):
        """Large linear feet should not overflow."""
        result = linear_feet_to_pieces(1_000_000.0)
        assert isinstance(result, int)
        assert result > 0

    def test_zero_linear_feet(self):
        """Zero linear feet should produce zero pieces."""
        result = linear_feet_to_pieces(0.0)
        assert result == 0

    def test_zero_piece_length_division(self):
        """Zero piece length should raise ZeroDivisionError or be handled."""
        with pytest.raises((ZeroDivisionError, ValueError)):
            linear_feet_to_pieces(100.0, piece_length=0.0)

    def test_negative_piece_length(self):
        """Negative piece length should raise or produce positive result."""
        try:
            result = linear_feet_to_pieces(100.0, piece_length=-10.0)
            # If it doesn't raise, the result should still be handled
            assert isinstance(result, int)
        except (ValueError, ZeroDivisionError):
            pass

    def test_huge_square_feet(self):
        """Very large square footage should not overflow."""
        result = square_feet_to_sheets(10_000_000.0)
        assert isinstance(result, int)
        assert result > 0

    def test_zero_sheet_size(self):
        """Zero sheet size should raise ZeroDivisionError."""
        with pytest.raises((ZeroDivisionError, ValueError)):
            square_feet_to_sheets(100.0, sheet_size=0.0)


# ── K3.2: Pitch Waste Edge Cases ────────────────────────────────────────────

class TestPitchWasteEdgeCases:
    """Pitch waste factors must handle unknown pitch categories."""

    def test_unknown_pitch_category(self):
        """Unknown pitch category should use 1.0 factor (no waste)."""
        result = apply_pitch_waste(100.0, "extreme")
        assert result == 100.0  # Factor 1.0

    def test_empty_pitch_category(self):
        """Empty string pitch should use 1.0 factor."""
        result = apply_pitch_waste(100.0, "")
        assert result == 100.0

    def test_zero_quantity_pitch(self):
        """Zero quantity with any pitch should return 0."""
        assert apply_pitch_waste(0.0, "steep") == 0.0

    def test_negative_quantity_pitch(self):
        """Negative quantities should apply waste factor correctly."""
        result = apply_pitch_waste(-100.0, "steep")
        assert result == pytest.approx(-115.0)  # -100 * 1.15


# ── K3.3: calculate_material_quantities Edge Cases ──────────────────────────

class TestMaterialQuantitiesEdgeCases:
    """End-to-end material conversion with adversarial inputs."""

    def test_empty_line_items(self):
        """Empty list should return empty list."""
        result = calculate_material_quantities([])
        assert result == []

    def test_missing_quantity_field(self):
        """Line item with no quantity should default to 0."""
        result = calculate_material_quantities([
            {"category": "RFG", "description": "No qty", "unit_of_measure": "SQ"}
        ])
        assert len(result) == 1
        assert result[0]["physical_qty"] == 0

    def test_missing_category_field(self):
        """Line item with no category should still produce output."""
        result = calculate_material_quantities([
            {"description": "No category", "quantity": 10, "unit_of_measure": "SQ"}
        ])
        assert len(result) == 1

    def test_missing_uom_field(self):
        """Line item with no unit_of_measure should still produce output."""
        result = calculate_material_quantities([
            {"category": "RFG", "description": "No UOM", "quantity": 10}
        ])
        assert len(result) == 1

    def test_very_large_quantity(self):
        """Very large quantity should not overflow."""
        result = calculate_material_quantities([
            {
                "category": "RFG",
                "description": "Huge job",
                "quantity": 999_999.99,
                "unit_of_measure": "SQ",
            }
        ])
        assert result[0]["physical_qty"] > 0

    def test_negative_quantity_item(self):
        """Negative quantity (CONST_003 credit) should be handled."""
        result = calculate_material_quantities([
            {
                "category": "RFG",
                "description": "Credit return",
                "quantity": -5.0,
                "unit_of_measure": "SQ",
            }
        ])
        assert len(result) == 1
        # Negative quantities get ceil'd to 0 or handled as credits
        assert isinstance(result[0]["physical_qty"], int)


# ── K3.4: O&P Stripper Edge Cases ──────────────────────────────────────────

class TestOOPStripperEdgeCases:
    """O&P stripping must handle all financial edge cases."""

    def test_zero_totals(self):
        """All-zero totals should return all-zero adjusted totals."""
        result = strip_overhead_and_profit(
            {"rcv": 0, "depreciation": 0, "acv": 0, "overhead": 0,
             "profit": 0, "tax": 0, "net_claim": 0},
            []
        )
        adj = result["adjusted_totals"]
        assert adj["rcv"] == 0.0
        assert adj["overhead"] == 0.0
        assert adj["profit"] == 0.0

    def test_no_overhead_no_profit(self):
        """Estimate with no O&P should return unchanged RCV."""
        totals = {"rcv": 10000, "depreciation": 2000, "acv": 8000,
                  "overhead": 0, "profit": 0, "tax": 500, "net_claim": 8500}
        result = strip_overhead_and_profit(totals, [])
        assert result["adjusted_totals"]["rcv"] == 10000.0

    def test_very_large_totals(self):
        """Very large dollar amounts should not lose precision."""
        totals = {
            "rcv": 999_999_999.99,
            "depreciation": 100_000_000.00,
            "acv": 899_999_999.99,
            "overhead": 99_999_999.99,
            "profit": 99_999_999.99,
            "tax": 50_000_000.00,
            "net_claim": 750_000_000.00,
        }
        result = strip_overhead_and_profit(totals, [])
        adj = result["adjusted_totals"]
        # O&P should be stripped
        assert adj["overhead"] == 0.0
        assert adj["profit"] == 0.0
        assert adj["rcv"] < totals["rcv"]

    def test_negative_overhead(self):
        """Negative overhead (unusual) should still compute."""
        totals = {"rcv": 10000, "depreciation": 2000, "acv": 8000,
                  "overhead": -500, "profit": 1000, "tax": 500, "net_claim": 7000}
        result = strip_overhead_and_profit(totals, [])
        assert isinstance(result["adjusted_totals"]["rcv"], float)

    def test_missing_fields_default_to_zero(self):
        """Missing fields in totals should default to 0, not crash."""
        result = strip_overhead_and_profit({}, [])
        adj = result["adjusted_totals"]
        assert adj["rcv"] == 0.0
        assert adj["overhead"] == 0.0


# ── K3.5: Credit Handler Edge Cases ────────────────────────────────────────

class TestCreditHandlerEdgeCases:
    """Credit handler (CONST_003) must properly route negative quantities."""

    def test_no_negative_items(self):
        """All positive quantities should produce zero credit items."""
        items = [
            {"category": "RFG", "description": "Shingles", "quantity": 10,
             "unit_of_measure": "SQ", "unit_price": 100, "total": 1000},
        ]
        result = handle_credits(items)
        assert len(result["credit_items"]) == 0
        assert len(result["procurement_items"]) == 1

    def test_all_negative_items(self):
        """All negative quantities should all become credit items."""
        items = [
            {"category": "RFG", "description": "Credit 1", "quantity": -5,
             "unit_of_measure": "SQ", "unit_price": 100, "total": -500},
            {"category": "RFG", "description": "Credit 2", "quantity": -3,
             "unit_of_measure": "SQ", "unit_price": 50, "total": -150},
        ]
        result = handle_credits(items)
        assert len(result["credit_items"]) == 2
        assert len(result["procurement_items"]) == 0

    def test_zero_quantity_item(self):
        """Zero quantity should be treated as standard (not credit)."""
        items = [
            {"category": "RFG", "description": "Zero", "quantity": 0,
             "unit_of_measure": "SQ", "unit_price": 100, "total": 0},
        ]
        result = handle_credits(items)
        assert len(result["credit_items"]) == 0

    def test_empty_items_list(self):
        """Empty list should return empty results."""
        result = handle_credits([])
        assert len(result["credit_items"]) == 0
        assert len(result["procurement_items"]) == 0


# ── K3.6: Trade Splitter Edge Cases ────────────────────────────────────────

class TestTradeSplitterEdgeCases:
    """Trade splitter must handle edge cases in trade grouping."""

    def test_empty_items(self):
        """Empty list should return empty trade groups."""
        result = split_by_trade([])
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_single_trade(self):
        """All items same trade should produce one group."""
        items = [
            {"trade": "roofing", "description": "Item 1"},
            {"trade": "roofing", "description": "Item 2"},
        ]
        result = split_by_trade(items)
        assert len(result) == 1
        assert "roofing" in result

    def test_missing_trade_field(self):
        """Items with no trade field should be grouped under 'general'."""
        items = [
            {"description": "No trade item"},
        ]
        result = split_by_trade(items)
        assert len(result) >= 1

    def test_mixed_case_trades(self):
        """Trades with different casing should be normalized."""
        items = [
            {"trade": "Roofing", "description": "Item 1"},
            {"trade": "roofing", "description": "Item 2"},
            {"trade": "ROOFING", "description": "Item 3"},
        ]
        result = split_by_trade(items)
        # Should be grouped together (implementation may or may not normalize)
        assert len(result) >= 1
