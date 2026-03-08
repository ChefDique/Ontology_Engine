"""Tests for Semantic Extractor — TASK_B2."""

import json
import pytest
from unittest.mock import patch

from ontology_engine.node2_extraction.extractor import (
    extract_estimate,
    _parse_llm_response,
    _validate_extraction,
    ExtractionError,
)


# ── Sample valid extraction output ──────────────────────────────────────────

VALID_EXTRACTION = {
    "header": {
        "estimate_number": "EST-2024-001",
        "claim_number": "CLM-12345",
        "carrier": "State Farm",
        "property_address": "REDACTED",
        "loss_date": "2024-01-15",
    },
    "line_items": [
        {
            "category": "RFG",
            "selector": "RFG_SHNG",
            "description": "Remove & replace shingles - 3 tab",
            "quantity": 32.33,
            "unit_of_measure": "SQ",
            "unit_price": 185.50,
            "total": 5996.72,
            "has_override_note": False,
            "f9_note_text": None,
        },
        {
            "category": "GUT",
            "selector": "GUT_ALM",
            "description": "Aluminum gutters - 5 inch",
            "quantity": 120.0,
            "unit_of_measure": "LF",
            "unit_price": 8.75,
            "total": 1050.0,
            "has_override_note": True,
            "f9_note_text": "F9: Price adjusted per local market",
        },
    ],
    "totals": {
        "rcv": 7046.72,
        "depreciation": 1200.0,
        "acv": 5846.72,
        "overhead": 704.67,
        "profit": 704.67,
        "tax": 352.34,
        "net_claim": 6903.39,
    },
}


class TestParseLLMResponse:
    def test_parses_clean_json(self):
        raw = json.dumps(VALID_EXTRACTION)
        result = _parse_llm_response(raw)
        assert result == VALID_EXTRACTION

    def test_strips_markdown_fences(self):
        raw = f"```json\n{json.dumps(VALID_EXTRACTION)}\n```"
        result = _parse_llm_response(raw)
        assert result == VALID_EXTRACTION

    def test_strips_whitespace(self):
        raw = f"  \n{json.dumps(VALID_EXTRACTION)}\n  "
        result = _parse_llm_response(raw)
        assert result == VALID_EXTRACTION

    def test_invalid_json_raises(self):
        with pytest.raises(ExtractionError, match="invalid JSON"):
            _parse_llm_response("not json at all")

    def test_empty_response_raises(self):
        with pytest.raises(ExtractionError, match="invalid JSON"):
            _parse_llm_response("")


class TestValidateExtraction:
    def test_valid_data_passes(self):
        _validate_extraction(VALID_EXTRACTION)  # Should not raise

    def test_missing_header_raises(self):
        data = {**VALID_EXTRACTION, "header": None}
        # header being None should fail
        with pytest.raises(ExtractionError, match="schema validation"):
            _validate_extraction({"line_items": VALID_EXTRACTION["line_items"],
                                  "totals": VALID_EXTRACTION["totals"]})

    def test_missing_line_items_raises(self):
        with pytest.raises(ExtractionError, match="schema validation"):
            _validate_extraction({"header": VALID_EXTRACTION["header"],
                                  "totals": VALID_EXTRACTION["totals"]})

    def test_empty_line_items_raises(self):
        data = {**VALID_EXTRACTION, "line_items": []}
        with pytest.raises(ExtractionError, match="schema validation"):
            _validate_extraction(data)

    def test_invalid_category_code_raises(self):
        bad_items = [{
            **VALID_EXTRACTION["line_items"][0],
            "category": "INVALID_CODE",
        }]
        data = {**VALID_EXTRACTION, "line_items": bad_items}
        with pytest.raises(ExtractionError, match="schema validation"):
            _validate_extraction(data)


class TestExtractEstimate:
    @patch("ontology_engine.node2_extraction.extractor._call_llm")
    def test_full_pipeline_with_mock(self, mock_llm):
        mock_llm.return_value = json.dumps(VALID_EXTRACTION)
        chunks = [{"chunk_text": "Sample Xactimate text..."}]
        result = extract_estimate(chunks)
        assert result["header"]["estimate_number"] == "EST-2024-001"
        assert len(result["line_items"]) == 2

    @patch("ontology_engine.node2_extraction.extractor._call_llm")
    def test_invalid_llm_response_raises(self, mock_llm):
        mock_llm.return_value = '{"bad": "data"}'
        chunks = [{"chunk_text": "text"}]
        with pytest.raises(ExtractionError):
            extract_estimate(chunks)

    def test_no_provider_raises_not_implemented(self):
        chunks = [{"chunk_text": "text"}]
        with pytest.raises(NotImplementedError):
            extract_estimate(chunks, provider="openai")
