"""Tests for contract validators."""

import pytest
from ontology_engine.contracts.validators import validate_contract, ContractViolation


class TestNode1To2Contract:
    def test_valid_data_passes(self):
        data = {
            "text": "Sample extracted text from PDF",
            "method": "native",
            "confidence": 0.95,
            "page_count": 3,
            "pii_redacted": True,
        }
        assert validate_contract(data, "node1_to_2") is True

    def test_missing_required_field_fails(self):
        data = {"text": "Some text", "method": "native"}  # missing confidence, page_count, pii_redacted
        with pytest.raises(ContractViolation):
            validate_contract(data, "node1_to_2")

    def test_pii_not_redacted_fails(self):
        data = {
            "text": "Text with PII",
            "method": "native",
            "confidence": 0.9,
            "page_count": 1,
            "pii_redacted": False,  # Must be True
        }
        with pytest.raises(ContractViolation):
            validate_contract(data, "node1_to_2")

    def test_unknown_contract_raises_valueerror(self):
        with pytest.raises(ValueError):
            validate_contract({}, "nonexistent_contract")
