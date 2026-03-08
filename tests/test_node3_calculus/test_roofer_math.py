"""Tests for Roofer Math — deterministic conversion functions."""

import math
import pytest
from ontology_engine.node3_calculus.roofer_math import (
    squares_to_bundles,
    linear_feet_to_pieces,
    apply_pitch_waste,
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
