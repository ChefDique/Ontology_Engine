"""Tests for Credit Handler — TASK_B5."""

from ontology_engine.node3_calculus.credit_handler import handle_credits


class TestHandleCredits:
    def test_positive_items_to_procurement(self):
        items = [
            {"category": "RFG", "quantity": 10.0, "description": "Shingles"},
            {"category": "GUT", "quantity": 50.0, "description": "Gutters"},
        ]
        result = handle_credits(items)
        assert len(result["procurement_items"]) == 2
        assert len(result["credit_items"]) == 0

    def test_negative_items_to_credits(self):
        items = [
            {"category": "RFG", "quantity": -5.0, "description": "Credit: Shingles"},
        ]
        result = handle_credits(items)
        assert len(result["procurement_items"]) == 0
        assert len(result["credit_items"]) == 1
        credit = result["credit_items"][0]
        assert credit["transaction_type"] == "credit_return"
        assert credit["quantity"] == 5.0  # Stored as positive
        assert credit["original_quantity"] == -5.0

    def test_mixed_items_split_correctly(self):
        items = [
            {"category": "RFG", "quantity": 32.0, "description": "Shingles"},
            {"category": "RFG", "quantity": -5.0, "description": "Credit shingles"},
            {"category": "GUT", "quantity": 120.0, "description": "Gutters"},
            {"category": "SID", "quantity": -10.0, "description": "Credit siding"},
        ]
        result = handle_credits(items)
        assert len(result["procurement_items"]) == 2
        assert len(result["credit_items"]) == 2

    def test_zero_quantity_excluded(self):
        items = [
            {"category": "RFG", "quantity": 0.0, "description": "Zero item"},
            {"category": "GUT", "quantity": 10.0, "description": "Gutters"},
        ]
        result = handle_credits(items)
        assert len(result["procurement_items"]) == 1
        assert len(result["credit_items"]) == 0

    def test_empty_input(self):
        result = handle_credits([])
        assert result["procurement_items"] == []
        assert result["credit_items"] == []

    def test_credit_preserves_original_fields(self):
        items = [{
            "category": "RFG",
            "quantity": -3.0,
            "description": "Credit: removed shingles",
            "unit_of_measure": "SQ",
            "unit_price": 185.50,
        }]
        result = handle_credits(items)
        credit = result["credit_items"][0]
        assert credit["unit_of_measure"] == "SQ"
        assert credit["unit_price"] == 185.50
        assert credit["transaction_type"] == "credit_return"
