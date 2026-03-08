"""Tests for Trade Splitter — TASK_B7."""

from ontology_engine.node3_calculus.trade_splitter import split_by_trade


class TestSplitByTrade:
    def test_single_trade(self):
        items = [
            {"category": "RFG", "description": "Shingles"},
            {"category": "GUT", "description": "Gutters"},
        ]
        result = split_by_trade(items)
        # Both RFG and GUT are "roofing" trade
        assert "roofing" in result
        assert len(result["roofing"]) == 2

    def test_multiple_trades(self):
        items = [
            {"category": "RFG", "description": "Shingles"},
            {"category": "ELC", "description": "Outlet"},
            {"category": "PLM", "description": "Faucet"},
        ]
        result = split_by_trade(items)
        assert len(result) == 3
        assert "roofing" in result
        assert "electrical" in result
        assert "plumbing" in result

    def test_unknown_code_goes_to_general(self):
        items = [{"category": "UNKNOWN", "description": "Mystery item"}]
        result = split_by_trade(items)
        assert "general" in result

    def test_preserves_item_data(self):
        items = [{"category": "RFG", "description": "Shingles", "quantity": 10}]
        result = split_by_trade(items)
        assert result["roofing"][0]["quantity"] == 10

    def test_empty_input(self):
        result = split_by_trade([])
        assert result == {}

    def test_item_with_trade_field_used_as_fallback(self):
        """If code is unknown but item has 'trade' field, use it."""
        items = [{"category": "ZZZ", "description": "Custom", "trade": "custom_trade"}]
        result = split_by_trade(items)
        assert "custom_trade" in result
