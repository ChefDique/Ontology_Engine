"""Integration tests for the pipeline orchestrator (TASK_F4).

Tests the full pipeline wiring, contract validation, and error handling.
Uses mocked node implementations since Nodes 2-4 depend on external services.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ontology_engine.pipeline import (
    ContractViolationError,
    PipelineError,
    _build_hitl_flags,
    _get_adapter,
    _validate_contract,
    run_pipeline,
)
from ontology_engine.contracts.schemas import (
    NODE_1_TO_2_SCHEMA,
    NODE_2_TO_3_SCHEMA,
    NODE_3_TO_4_SCHEMA,
)


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def node1_output():
    """Valid Node 1 → Node 2 output."""
    return {
        "text": "Sample redacted estimate text",
        "method": "native",
        "confidence": 0.95,
        "page_count": 3,
        "pii_redacted": True,
        "chunks": [
            {
                "chunk_text": "Sample redacted estimate text chunk 1",
                "chunk_index": 0,
                "token_count": 50,
            },
        ],
    }


@pytest.fixture
def node2_output():
    """Valid Node 2 → Node 3 output."""
    return {
        "header": {
            "estimate_number": "EST-001",
            "claim_number": "CLM-123",
            "carrier": "StateFarm",
            "loss_date": "2024-01-15",
        },
        "line_items": [
            {
                "category": "RFG",
                "selector": "RFG SHNG",
                "description": "Remove & replace comp shingles 3-tab 25 yr",
                "quantity": 24.5,
                "unit_of_measure": "SQ",
                "unit_price": 195.50,
                "total": 4789.75,
                "has_override_note": False,
                "f9_note_text": None,
            },
            {
                "category": "GUT",
                "description": "Remove & replace aluminum seamless gutter",
                "quantity": 120.0,
                "unit_of_measure": "LF",
                "unit_price": 8.50,
                "total": 1020.00,
                "has_override_note": False,
                "f9_note_text": None,
            },
        ],
        "totals": {
            "rcv": 5809.75,
            "depreciation": 580.98,
            "acv": 5228.77,
            "overhead": 580.98,
            "profit": 580.98,
            "tax": 464.78,
            "net_claim": 5693.55,
        },
    }


@pytest.fixture
def node3_output():
    """Valid Node 3 → Node 4 output."""
    return {
        "header": {"estimate_number": "EST-001"},
        "procurement_items": [
            {
                "category": "RFG",
                "description": "Comp shingles 3-tab 25 yr",
                "physical_qty": 78,
                "physical_unit": "bundles",
                "trade": "roofing",
                "unit_cost": 195.50,
            },
        ],
        "credit_items": [],
        "adjusted_totals": {
            "rcv": 4647.79,
            "depreciation": 580.98,
            "acv": 4066.81,
            "overhead": 0.0,
            "profit": 0.0,
            "tax": 371.82,
            "net_claim": 4438.63,
        },
        "hitl_flags": [],
    }


# ── Contract Validation Tests ─────────────────────────────────────────────

class TestContractValidation:
    """Tests for inter-node contract validation."""

    def test_valid_node1_to_node2(self, node1_output):
        """Valid Node 1 output passes contract validation."""
        _validate_contract(node1_output, NODE_1_TO_2_SCHEMA, "Node1", "Node2")

    def test_valid_node2_to_node3(self, node2_output):
        """Valid Node 2 output passes contract validation."""
        _validate_contract(node2_output, NODE_2_TO_3_SCHEMA, "Node2", "Node3")

    def test_valid_node3_to_node4(self, node3_output):
        """Valid Node 3 output passes contract validation."""
        _validate_contract(node3_output, NODE_3_TO_4_SCHEMA, "Node3", "Node4")

    def test_invalid_node1_missing_text(self, node1_output):
        """Node 1 output missing 'text' fails validation."""
        del node1_output["text"]
        with pytest.raises(ContractViolationError, match="Node1→Node2"):
            _validate_contract(node1_output, NODE_1_TO_2_SCHEMA, "Node1", "Node2")

    def test_invalid_node2_missing_line_items(self, node2_output):
        """Node 2 output missing 'line_items' fails validation."""
        del node2_output["line_items"]
        with pytest.raises(ContractViolationError, match="Node2→Node3"):
            _validate_contract(node2_output, NODE_2_TO_3_SCHEMA, "Node2", "Node3")

    def test_invalid_node3_missing_procurement(self, node3_output):
        """Node 3 output missing 'procurement_items' fails validation."""
        del node3_output["procurement_items"]
        with pytest.raises(ContractViolationError, match="Node3→Node4"):
            _validate_contract(node3_output, NODE_3_TO_4_SCHEMA, "Node3", "Node4")

    def test_node1_pii_must_be_true(self, node1_output):
        """Node 1 output with pii_redacted=False fails validation."""
        node1_output["pii_redacted"] = False
        with pytest.raises(ContractViolationError):
            _validate_contract(node1_output, NODE_1_TO_2_SCHEMA, "Node1", "Node2")

    def test_node1_confidence_bounds(self, node1_output):
        """Node 1 confidence must be within 0.0-1.0."""
        node1_output["confidence"] = 1.5
        with pytest.raises(ContractViolationError):
            _validate_contract(node1_output, NODE_1_TO_2_SCHEMA, "Node1", "Node2")


# ── HITL Flag Tests ───────────────────────────────────────────────────────

class TestHITLFlags:
    """Tests for HITL flag generation."""

    def test_no_flags_high_confidence(self, node3_output):
        """High confidence with no credits generates no flags."""
        flags = _build_hitl_flags(node3_output, confidence=0.95)
        assert len(flags) == 0

    def test_low_confidence_flag(self, node3_output):
        """Low confidence generates a flag."""
        flags = _build_hitl_flags(node3_output, confidence=0.5)
        assert len(flags) == 1
        assert flags[0]["type"] == "low_confidence"

    def test_credit_items_flag(self, node3_output):
        """Credit items generate HITL flags."""
        node3_output["credit_items"] = [
            {"transaction_type": "credit_return", "description": "Removed item"}
        ]
        flags = _build_hitl_flags(node3_output, confidence=0.95)
        assert len(flags) == 1
        assert flags[0]["type"] == "credit_return"

    def test_multiple_flags(self, node3_output):
        """Multiple conditions produce multiple flags."""
        node3_output["credit_items"] = [
            {"transaction_type": "credit_return", "description": "Item 1"},
            {"transaction_type": "credit_return", "description": "Item 2"},
        ]
        flags = _build_hitl_flags(node3_output, confidence=0.5)
        # 2 credit flags + 1 low_confidence
        assert len(flags) == 3


# ── Adapter Dispatch Tests ────────────────────────────────────────────────

class TestAdapterDispatch:
    """Tests for CRM adapter resolution."""

    def test_buildertrend_adapter(self):
        """Buildertrend adapter resolves correctly."""
        from ontology_engine.node4_output.buildertrend_csv import BuildertrendAdapter
        adapter = _get_adapter("buildertrend")
        assert isinstance(adapter, BuildertrendAdapter)

    def test_unknown_crm_raises(self):
        """Unknown CRM raises PipelineError."""
        with pytest.raises(PipelineError, match="Unknown target CRM"):
            _get_adapter("salesforce")

    def test_case_insensitive(self):
        """Adapter lookup is case-insensitive."""
        from ontology_engine.node4_output.buildertrend_csv import BuildertrendAdapter
        adapter = _get_adapter("BUILDERTREND")
        assert isinstance(adapter, BuildertrendAdapter)

    def test_whitespace_stripped(self):
        """Adapter lookup strips whitespace."""
        from ontology_engine.node4_output.buildertrend_csv import BuildertrendAdapter
        adapter = _get_adapter("  buildertrend  ")
        assert isinstance(adapter, BuildertrendAdapter)


# ── Pipeline Integration Tests ────────────────────────────────────────────

class TestPipelineIntegration:
    """End-to-end pipeline integration tests with mocked nodes."""

    @patch("ontology_engine.node2_extraction.extractor.extract_estimate")
    @patch("ontology_engine.node1_ingestion.ingest")
    def test_full_pipeline_success(
        self, mock_ingest, mock_extract, node1_output, node2_output, tmp_path
    ):
        """Full pipeline completes successfully with mocked nodes."""
        mock_ingest.return_value = node1_output
        mock_extract.return_value = node2_output

        input_pdf = tmp_path / "test.pdf"
        input_pdf.write_text("fake pdf")

        result = run_pipeline(
            input_path=input_pdf,
            target_crm="buildertrend",
            output_dir=tmp_path,
        )

        assert result["success"] is True
        assert Path(result["output_path"]).exists()
        assert result["metadata"]["target_crm"] == "buildertrend"
        assert "duration_seconds" in result["metadata"]
        assert "node1_ingestion" in result["metadata"]["nodes_completed"]
        assert "node4_output" in result["metadata"]["nodes_completed"]

    @patch("ontology_engine.node1_ingestion.ingest")
    def test_pipeline_contract_failure(self, mock_ingest, tmp_path):
        """Pipeline raises on contract violation."""
        # Return invalid Node 1 output (missing required fields)
        mock_ingest.return_value = {"text": "hello"}

        input_pdf = tmp_path / "test.pdf"
        input_pdf.write_text("fake pdf")

        with pytest.raises(ContractViolationError, match="Node1→Node2"):
            run_pipeline(input_path=input_pdf, target_crm="buildertrend")

    @patch("ontology_engine.node2_extraction.extractor.extract_estimate")
    @patch("ontology_engine.node1_ingestion.ingest")
    def test_pipeline_hitl_flags_on_low_confidence(
        self, mock_ingest, mock_extract, node1_output, node2_output, tmp_path
    ):
        """Pipeline flags low confidence for HITL review."""
        node1_output["confidence"] = 0.3  # Below threshold
        mock_ingest.return_value = node1_output
        mock_extract.return_value = node2_output

        input_pdf = tmp_path / "test.pdf"
        input_pdf.write_text("fake pdf")

        result = run_pipeline(
            input_path=input_pdf,
            target_crm="buildertrend",
            output_dir=tmp_path,
        )

        assert result["success"] is True
        assert len(result["hitl_items"]) > 0

    @patch("ontology_engine.node2_extraction.extractor.extract_estimate")
    @patch("ontology_engine.node1_ingestion.ingest")
    def test_pipeline_output_file_name(
        self, mock_ingest, mock_extract, node1_output, node2_output, tmp_path
    ):
        """Output file is named with estimate number and CRM."""
        mock_ingest.return_value = node1_output
        mock_extract.return_value = node2_output

        input_pdf = tmp_path / "test.pdf"
        input_pdf.write_text("fake pdf")

        result = run_pipeline(
            input_path=input_pdf,
            target_crm="buildertrend",
            output_dir=tmp_path,
        )

        output_path = Path(result["output_path"])
        assert "EST-001" in output_path.name
        assert "buildertrend" in output_path.name
        assert output_path.suffix == ".csv"
