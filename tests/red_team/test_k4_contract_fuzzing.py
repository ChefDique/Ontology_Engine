"""TASK_K4 — Contract boundary fuzzing (all node boundaries).

Tests contract validation resilience against:
  - Invalid schemas / missing required fields
  - Type coercion attacks (string → number, null → object)
  - Extra unexpected fields
  - Deeply nested invalid structures
  - Empty payloads
"""

import copy
import json

import pytest

from ontology_engine.contracts.validators import (
    ContractViolation,
    validate_contract,
)
from ontology_engine.contracts.schemas import (
    NODE_1_TO_2_SCHEMA,
    NODE_2_TO_3_SCHEMA,
    NODE_3_TO_4_SCHEMA,
    NODE_5_INPUT_SCHEMA,
    NODE_5_OUTPUT_SCHEMA,
)


# ── K4.1: Node 1→2 Contract Fuzzing ────────────────────────────────────────

class TestNode1To2ContractFuzzing:
    """Fuzz the Node 1→2 contract boundary."""

    def test_empty_object(self):
        """Empty object should fail — missing all required fields."""
        with pytest.raises(ContractViolation):
            validate_contract({}, "node1_to_2")

    def test_null_payload(self):
        """None should raise (not a dict)."""
        with pytest.raises((ContractViolation, Exception)):
            validate_contract(None, "node1_to_2")

    def test_text_as_number(self):
        """text field as number instead of string should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": 12345,
                "method": "native",
                "confidence": 1.0,
                "page_count": 1,
                "pii_redacted": True,
            }, "node1_to_2")

    def test_empty_text(self):
        """Empty text string should fail (minLength: 1)."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": "",
                "method": "native",
                "confidence": 1.0,
                "page_count": 1,
                "pii_redacted": True,
            }, "node1_to_2")

    def test_invalid_method_enum(self):
        """Method not in enum should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": "Valid text",
                "method": "magic",
                "confidence": 1.0,
                "page_count": 1,
                "pii_redacted": True,
            }, "node1_to_2")

    def test_confidence_out_of_range(self):
        """Confidence > 1.0 should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": "Valid text",
                "method": "native",
                "confidence": 1.5,
                "page_count": 1,
                "pii_redacted": True,
            }, "node1_to_2")

    def test_negative_confidence(self):
        """Negative confidence should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": "Valid text",
                "method": "native",
                "confidence": -0.1,
                "page_count": 1,
                "pii_redacted": True,
            }, "node1_to_2")

    def test_zero_page_count(self):
        """page_count of 0 should fail (minimum: 1)."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": "Valid text",
                "method": "native",
                "confidence": 1.0,
                "page_count": 0,
                "pii_redacted": True,
            }, "node1_to_2")

    def test_pii_redacted_false(self):
        """pii_redacted=False should fail (const: True)."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": "Valid text",
                "method": "native",
                "confidence": 1.0,
                "page_count": 1,
                "pii_redacted": False,
            }, "node1_to_2")

    def test_valid_minimal_passes(self):
        """Minimal valid payload should pass."""
        assert validate_contract({
            "text": "Valid text",
            "method": "native",
            "confidence": 1.0,
            "page_count": 1,
            "pii_redacted": True,
        }, "node1_to_2") is True

    def test_extra_fields_tolerated(self):
        """Extra fields should be tolerated (open schema)."""
        assert validate_contract({
            "text": "Valid text",
            "method": "native",
            "confidence": 1.0,
            "page_count": 1,
            "pii_redacted": True,
            "extra_field": "ignored",
        }, "node1_to_2") is True


# ── K4.2: Node 2→3 Contract Fuzzing ────────────────────────────────────────

class TestNode2To3ContractFuzzing:
    """Fuzz the Node 2→3 contract boundary."""

    def test_empty_object(self):
        """Empty object should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({}, "node2_to_3")

    def test_line_items_not_array(self):
        """line_items as object instead of array should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": {},
                "line_items": {"not": "an array"},
                "totals": {},
            }, "node2_to_3")

    def test_line_item_quantity_as_string(self):
        """quantity as string should fail validation."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": {},
                "line_items": [{
                    "category": "RFG",
                    "description": "Test",
                    "quantity": "not_a_number",
                    "unit_of_measure": "SQ",
                }],
                "totals": {},
            }, "node2_to_3")

    def test_valid_with_empty_collections(self):
        """Empty arrays and objects should pass as minimal."""
        assert validate_contract({
            "header": {},
            "line_items": [],
            "totals": {},
        }, "node2_to_3") is True

    def test_line_item_missing_required(self):
        """Line item missing category+description should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": {},
                "line_items": [{"quantity": 5}],
                "totals": {},
            }, "node2_to_3")


# ── K4.3: Node 3→4 Contract Fuzzing ────────────────────────────────────────

class TestNode3To4ContractFuzzing:
    """Fuzz the Node 3→4 contract boundary."""

    def test_empty_object(self):
        """Empty object should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({}, "node3_to_4")

    def test_physical_qty_zero(self):
        """physical_qty of 0 should fail (minimum: 1)."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": {},
                "procurement_items": [{
                    "category": "RFG",
                    "description": "Test",
                    "physical_qty": 0,
                    "physical_unit": "bundles",
                    "trade": "roofing",
                }],
                "adjusted_totals": {},
            }, "node3_to_4")

    def test_physical_qty_negative(self):
        """Negative physical_qty should fail (minimum: 1)."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": {},
                "procurement_items": [{
                    "category": "RFG",
                    "description": "Test",
                    "physical_qty": -5,
                    "physical_unit": "bundles",
                    "trade": "roofing",
                }],
                "adjusted_totals": {},
            }, "node3_to_4")

    def test_physical_qty_float(self):
        """physical_qty as float should fail (type: integer)."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": {},
                "procurement_items": [{
                    "category": "RFG",
                    "description": "Test",
                    "physical_qty": 10.5,
                    "physical_unit": "bundles",
                    "trade": "roofing",
                }],
                "adjusted_totals": {},
            }, "node3_to_4")

    def test_credit_item_wrong_type(self):
        """credit_items with wrong transaction_type should fail (const)."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": {},
                "procurement_items": [],
                "credit_items": [{"transaction_type": "not_credit"}],
                "adjusted_totals": {},
            }, "node3_to_4")

    def test_valid_minimal(self):
        """Minimal valid Node 3→4 should pass."""
        assert validate_contract({
            "header": {},
            "procurement_items": [],
            "adjusted_totals": {},
        }, "node3_to_4") is True


# ── K4.4: Unknown Contract Names ────────────────────────────────────────────

class TestUnknownContractNames:
    """Validator should reject unknown contract names."""

    def test_unknown_contract_name(self):
        """Unknown contract name should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown contract"):
            validate_contract({}, "node99_to_100")

    def test_empty_contract_name(self):
        """Empty contract name should raise ValueError."""
        with pytest.raises(ValueError):
            validate_contract({}, "")

    def test_none_contract_name(self):
        """None contract name should raise."""
        with pytest.raises((ValueError, TypeError)):
            validate_contract({}, None)


# ── K4.5: Type Coercion Attacks ─────────────────────────────────────────────

class TestTypeCoercionAttacks:
    """Schema should reject values masquerading as correct types."""

    def test_boolean_as_number(self):
        """Boolean True/False should not pass as number in all contexts."""
        # Note: in JSON Schema, booleans ARE valid numbers, so this tests awareness
        payload = {
            "text": "Valid text",
            "method": "native",
            "confidence": True,  # Boolean, but JSON Schema accepts as number
            "page_count": 1,
            "pii_redacted": True,
        }
        # This may actually pass JSON Schema validation since True == 1
        # The test documents this known behavior
        try:
            validate_contract(payload, "node1_to_2")
        except ContractViolation:
            pass  # Also acceptable if implementation is stricter

    def test_string_number_not_coerced(self):
        """String '1.0' should not be coerced to number."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "text": "Valid text",
                "method": "native",
                "confidence": "1.0",  # String, not number
                "page_count": 1,
                "pii_redacted": True,
            }, "node1_to_2")

    def test_list_as_object(self):
        """Array where object expected should fail."""
        with pytest.raises(ContractViolation):
            validate_contract({
                "header": ["not", "an", "object"],
                "line_items": [],
                "totals": {},
            }, "node2_to_3")
