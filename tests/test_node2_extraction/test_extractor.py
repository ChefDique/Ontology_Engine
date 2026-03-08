"""Tests for Semantic Extractor — TASK_B2 + TASK_G5.

Tests cover:
- JSON parsing (clean, markdown-fenced, whitespace)
- Schema validation (valid data, missing fields, invalid codes)
- Full pipeline with mocked Gemini responses
- Gemini-specific error handling (rate limits, safety, empty responses)
- Provider dispatch and configuration
"""

import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

from ontology_engine.node2_extraction.extractor import (
    extract_estimate,
    _call_llm,
    _parse_llm_response,
    _validate_extraction,
    ExtractionError,
    LLMProviderError,
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

SAMPLE_CHUNKS = [{"chunk_text": "Sample Xactimate estimate text..."}]


# ── Mock helpers ────────────────────────────────────────────────────────────

def _make_gemini_response(text, finish_reason="STOP", has_candidates=True):
    """Helper to create a mock Gemini API response."""
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = MagicMock()
    mock_candidate.finish_reason.name = finish_reason

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate] if has_candidates else []
    mock_response.text = text
    return mock_response


@pytest.fixture
def mock_genai():
    """Fixture that installs a mock google.generativeai in sys.modules.

    This allows tests to run without the google-generativeai SDK installed.
    The mock module provides configure(), GenerativeModel(), and
    GenerationConfig() — the same interface our code uses.

    IMPORTANT: Python's import machinery for `import google.generativeai as genai`
    resolves `google` first, then accesses `.generativeai` on it. We must:
    1. Set both `google` and `google.generativeai` in sys.modules
    2. Wire `google_mock.generativeai = genai_mock` so attribute access works
    """
    genai_mock = MagicMock()
    google_mock = MagicMock()
    google_mock.generativeai = genai_mock

    saved = {}
    modules_to_mock = {
        "google": google_mock,
        "google.generativeai": genai_mock,
    }
    for name, mod in modules_to_mock.items():
        saved[name] = sys.modules.get(name)
        sys.modules[name] = mod

    yield genai_mock

    for name, original in saved.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original


@pytest.fixture
def gemini_config_patches():
    """Fixture that patches ontology_engine.config with Gemini test values.

    Since config.py reads env vars at module load time, we need to patch
    the actual config module attributes, not just os.environ.
    """
    import ontology_engine.config as config
    patches = {
        "GOOGLE_API_KEY": "test-key-123",
        "GEMINI_MODEL": "gemini-2.0-flash",
        "GEMINI_TEMPERATURE": 0.1,
        "GEMINI_MAX_OUTPUT_TOKENS": 8192,
        "GEMINI_MAX_RETRIES": 3,
        "GEMINI_RETRY_DELAY": 0.01,  # Fast retries for tests
    }
    originals = {}
    for attr, value in patches.items():
        originals[attr] = getattr(config, attr, None)
        setattr(config, attr, value)

    yield config

    for attr, value in originals.items():
        if value is not None:
            setattr(config, attr, value)
        elif hasattr(config, attr):
            delattr(config, attr)


# ── Parse Tests ─────────────────────────────────────────────────────────────


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


# ── Validation Tests ────────────────────────────────────────────────────────


class TestValidateExtraction:
    def test_valid_data_passes(self):
        _validate_extraction(VALID_EXTRACTION)  # Should not raise

    def test_missing_header_raises(self):
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


# ── Provider Dispatch Tests ─────────────────────────────────────────────────


class TestCallLLMDispatch:
    @patch("ontology_engine.node2_extraction.extractor._call_gemini")
    def test_dispatches_to_gemini(self, mock_gemini):
        mock_gemini.return_value = json.dumps(VALID_EXTRACTION)
        result = _call_llm("system", "user", "gemini")
        mock_gemini.assert_called_once_with("system", "user")
        assert result == json.dumps(VALID_EXTRACTION)

    def test_unknown_provider_raises(self):
        with pytest.raises(NotImplementedError, match="not yet wired"):
            _call_llm("system", "user", "unsupported_provider")

    def test_openai_not_implemented(self):
        with pytest.raises(NotImplementedError, match="not yet wired"):
            _call_llm("system", "user", "openai")


# ── Full Pipeline Tests ─────────────────────────────────────────────────────


class TestExtractEstimate:
    @patch("ontology_engine.node2_extraction.extractor._call_llm")
    def test_full_pipeline_with_mock(self, mock_llm):
        mock_llm.return_value = json.dumps(VALID_EXTRACTION)
        result = extract_estimate(SAMPLE_CHUNKS, provider="gemini")
        assert result["header"]["estimate_number"] == "EST-2024-001"
        assert len(result["line_items"]) == 2

    @patch("ontology_engine.node2_extraction.extractor._call_llm")
    def test_invalid_llm_response_raises(self, mock_llm):
        mock_llm.return_value = '{"bad": "data"}'
        with pytest.raises(ExtractionError):
            extract_estimate(SAMPLE_CHUNKS, provider="gemini")

    @patch("ontology_engine.node2_extraction.extractor._call_llm")
    def test_multiple_chunks_concatenated(self, mock_llm):
        mock_llm.return_value = json.dumps(VALID_EXTRACTION)
        multi_chunks = [
            {"chunk_text": "Chunk 1 text"},
            {"chunk_text": "Chunk 2 text"},
            {"chunk_text": "Chunk 3 text"},
        ]
        extract_estimate(multi_chunks, provider="gemini")
        call_args = mock_llm.call_args
        user_prompt = call_args[1]["user_prompt"]
        assert "Chunk 1 text" in user_prompt
        assert "Chunk 2 text" in user_prompt
        assert "Chunk 3 text" in user_prompt


# ── Gemini-Specific Tests ───────────────────────────────────────────────────


class TestCallGemini:
    """Tests for the Gemini Flash integration — TASK_G5.

    Uses mock_genai (sys.modules mock) + gemini_config_patches (config attrs)
    to isolate tests from both the SDK and the .env file.
    """

    def test_missing_api_key_raises(self, mock_genai, gemini_config_patches):
        """Should raise LLMProviderError when GOOGLE_API_KEY is empty."""
        from ontology_engine.node2_extraction.extractor import _call_gemini
        gemini_config_patches.GOOGLE_API_KEY = ""
        with pytest.raises(LLMProviderError, match="GOOGLE_API_KEY not set"):
            _call_gemini("system prompt", "user prompt")

    def test_successful_gemini_call(self, mock_genai, gemini_config_patches):
        """Should return text from a successful Gemini response."""
        from ontology_engine.node2_extraction.extractor import _call_gemini

        mock_response = _make_gemini_response(json.dumps(VALID_EXTRACTION))
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = _call_gemini("system prompt", "user prompt")

        assert result == json.dumps(VALID_EXTRACTION)
        mock_genai.configure.assert_called_with(api_key="test-key-123")
        mock_model.generate_content.assert_called_once_with("user prompt")

    def test_safety_block_raises_provider_error(self, mock_genai, gemini_config_patches):
        """Should raise LLMProviderError when response blocked by safety."""
        from ontology_engine.node2_extraction.extractor import _call_gemini

        mock_response = _make_gemini_response("", finish_reason="SAFETY")
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(LLMProviderError, match="safety filters"):
            _call_gemini("system prompt", "user prompt")

    def test_no_candidates_raises_provider_error(self, mock_genai, gemini_config_patches):
        """Should raise LLMProviderError when no candidates returned."""
        from ontology_engine.node2_extraction.extractor import _call_gemini

        mock_response = _make_gemini_response("", has_candidates=False)
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(LLMProviderError, match="no candidates"):
            _call_gemini("system prompt", "user prompt")

    @patch("time.sleep")
    def test_rate_limit_retries(self, mock_sleep, mock_genai, gemini_config_patches):
        """Should retry on rate limit (429) errors with backoff."""
        from ontology_engine.node2_extraction.extractor import _call_gemini

        mock_success = _make_gemini_response(json.dumps(VALID_EXTRACTION))
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = [
            Exception("429 Resource Exhausted"),
            Exception("429 Resource Exhausted"),
            mock_success,
        ]
        mock_genai.GenerativeModel.return_value = mock_model

        result = _call_gemini("system prompt", "user prompt")

        assert result == json.dumps(VALID_EXTRACTION)
        assert mock_model.generate_content.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("time.sleep")
    def test_all_retries_exhausted_raises(self, mock_sleep, mock_genai, gemini_config_patches):
        """Should raise ExtractionError after all retries exhausted."""
        from ontology_engine.node2_extraction.extractor import _call_gemini

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("429 Resource Exhausted")
        mock_genai.GenerativeModel.return_value = mock_model

        gemini_config_patches.GEMINI_MAX_RETRIES = 2
        with pytest.raises(ExtractionError, match="failed after 2 attempts"):
            _call_gemini("system prompt", "user prompt")

    def test_max_tokens_finish_still_returns(self, mock_genai, gemini_config_patches):
        """Should return text even if truncated (validation catches bad JSON)."""
        from ontology_engine.node2_extraction.extractor import _call_gemini

        mock_response = _make_gemini_response(
            json.dumps(VALID_EXTRACTION), finish_reason="MAX_TOKENS"
        )
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = _call_gemini("system prompt", "user prompt")
        assert result == json.dumps(VALID_EXTRACTION)

    @patch("time.sleep")
    def test_transient_error_retries(self, mock_sleep, mock_genai, gemini_config_patches):
        """Should retry on transient/network errors."""
        from ontology_engine.node2_extraction.extractor import _call_gemini

        mock_success = _make_gemini_response(json.dumps(VALID_EXTRACTION))
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = [
            Exception("503 Service Unavailable"),
            mock_success,
        ]
        mock_genai.GenerativeModel.return_value = mock_model

        result = _call_gemini("system prompt", "user prompt")

        assert result == json.dumps(VALID_EXTRACTION)
        assert mock_model.generate_content.call_count == 2
