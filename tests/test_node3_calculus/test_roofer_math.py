"""Tests for Roofer Math — deterministic conversion functions."""

import math
import pytest
from ontology_engine.node3_calculus.roofer_math import (
    squares_to_bundles,
    linear_feet_to_pieces,
    apply_pitch_waste,
    square_feet_to_sheets,
    calculate_material_quantities,
)


class TestSquaresToBundles:
    def test_basic_conversion(self):
        assert squares_to_bundles(10.0) == 30  # 10 × 3 = 30

    def test_always_rounds_up(self):
        assert squares_to_bundles(10.1) == 31  # 10.1 × 3 = 30.3 → ceil = 31

    def test_with_waste_factor(self):
        # 10 × 3 × 1.15 = 34.5 → ceil = 35
        assert squares_to_bundles(10.0, waste_factor=1.15) == 35

    def test_fractional_squares(self):
        # 32.33 × 3 = 96.99 → ceil = 97
        assert squares_to_bundles(32.33) == 97

    def test_zero_squares(self):
        assert squares_to_bundles(0.0) == 0


class TestLinearFeetToPieces:
    def test_basic_conversion(self):
        assert linear_feet_to_pieces(100.0) == 10  # 100 / 10 = 10

    def test_always_rounds_up(self):
        assert linear_feet_to_pieces(101.0) == 11  # 101 / 10 = 10.1 → ceil = 11

    def test_custom_piece_length(self):
        assert linear_feet_to_pieces(25.0, piece_length=5.0) == 5


class TestApplyPitchWaste:
    def test_low_pitch(self):
        result = apply_pitch_waste(100.0, "low")
        assert result == pytest.approx(105.0)

    def test_steep_pitch(self):
        result = apply_pitch_waste(100.0, "steep")
        assert result == pytest.approx(115.0)

    def test_unknown_pitch_no_waste(self):
        result = apply_pitch_waste(100.0, "unknown")
        assert result == pytest.approx(100.0)


class TestSquareFeetToSheets:
    def test_exact_sheets(self):
        assert square_feet_to_sheets(128.0) == 4  # 128 / 32 = 4

    def test_rounds_up(self):
        assert square_feet_to_sheets(130.0) == 5  # 130 / 32 = 4.0625 → ceil = 5

    def test_single_sheet(self):
        assert square_feet_to_sheets(10.0) == 1


class TestCalculateMaterialQuantities:
    def test_roofing_conversion(self):
        items = [{
            "category": "RFG",
            "description": "Shingles 3-tab",
            "quantity": 10.0,
            "unit_of_measure": "SQ",
        }]
        result = calculate_material_quantities(items, pitch_category="low")
        assert len(result) == 1
        # 10 × 3 × 1.05 = 31.5 → ceil = 32
        assert result[0]["physical_qty"] == 32
        assert result[0]["physical_unit"] == "bundles"
        assert result[0]["trade"] == "roofing"

    def test_gutter_conversion(self):
        items = [{
            "category": "GUT",
            "description": "Aluminum gutters",
            "quantity": 120.0,
            "unit_of_measure": "LF",
        }]
        result = calculate_material_quantities(items)
        assert result[0]["physical_qty"] == 12  # 120 / 10 = 12
        assert result[0]["physical_unit"] == "pieces"

    def test_siding_conversion(self):
        items = [{
            "category": "SID",
            "description": "Vinyl siding panels",
            "quantity": 500.0,
            "unit_of_measure": "SF",
        }]
        result = calculate_material_quantities(items)
        assert result[0]["physical_qty"] == 16  # 500 / 32 = 15.625 → 16
        assert result[0]["physical_unit"] == "sheets"

    def test_unknown_category_fallback(self):
        items = [{
            "category": "XYZ",
            "description": "Unknown material",
            "quantity": 5.5,
            "unit_of_measure": "EA",
        }]
        result = calculate_material_quantities(items)
        assert result[0]["physical_qty"] == 6  # ceil(5.5)
        assert result[0]["trade"] == "general"

    def test_multiple_items_mixed_trades(self):
        items = [
            {"category": "RFG", "description": "Shingles", "quantity": 10.0, "unit_of_measure": "SQ"},
            {"category": "ELC", "description": "Outlet", "quantity": 3.0, "unit_of_measure": "EA"},
            {"category": "GUT", "description": "Gutters", "quantity": 50.0, "unit_of_measure": "LF"},
        ]
        result = calculate_material_quantities(items, pitch_category="medium")
        assert len(result) == 3
        assert result[0]["trade"] == "roofing"
        assert result[1]["trade"] == "electrical"
        assert result[2]["trade"] == "roofing"  # gutters are roofing trade

    def test_unit_cost_carried_forward(self):
        items = [{
            "category": "PLM",
            "description": "Fixture",
            "quantity": 2.0,
            "unit_of_measure": "EA",
            "unit_price": 150.0,
        }]
        result = calculate_material_quantities(items)
        assert result[0]["unit_cost"] == 150.0

    def test_steep_pitch_waste_applied(self):
        items = [{
            "category": "RFG",
            "description": "Shingles",
            "quantity": 10.0,
            "unit_of_measure": "SQ",
        }]
        result = calculate_material_quantities(items, pitch_category="steep")
        # 10 × 3 × 1.15 = 34.5 → ceil = 35
        assert result[0]["physical_qty"] == 35
