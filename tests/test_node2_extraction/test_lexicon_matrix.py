"""Tests for Lexicon Matrix — Xactimate code lookups."""

from ontology_engine.node2_extraction.lexicon_matrix import (
    LEXICON_MATRIX,
    lookup_code,
    get_trade,
)


class TestLookupCode:
    def test_known_code(self):
        result = lookup_code("RFG")
        assert result is not None
        assert result["trade"] == "roofing"
        assert result["default_uom"] == "SQ"

    def test_known_code_lowercase(self):
        result = lookup_code("rfg")
        assert result is not None
        assert result["trade"] == "roofing"

    def test_unknown_code_returns_none(self):
        assert lookup_code("XYZ") is None

    def test_all_codes_have_required_fields(self):
        required = {"description", "default_uom", "trade", "material_type"}
        for code, entry in LEXICON_MATRIX.items():
            missing = required - set(entry.keys())
            assert not missing, f"{code} missing: {missing}"


class TestGetTrade:
    def test_roofing_trade(self):
        assert get_trade("RFG") == "roofing"

    def test_gutters_are_roofing(self):
        assert get_trade("GUT") == "roofing"

    def test_plumbing_trade(self):
        assert get_trade("PLM") == "plumbing"

    def test_unknown_returns_none(self):
        assert get_trade("UNKNOWN") is None

    def test_all_lexicon_codes(self):
        """Every code in the matrix should return a non-None trade."""
        for code in LEXICON_MATRIX:
            trade = get_trade(code)
            assert trade is not None, f"{code} has no trade"
