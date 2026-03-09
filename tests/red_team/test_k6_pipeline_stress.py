"""TASK_K6 — End-to-end pipeline stress tests.

Tests pipeline-level resilience against:
  - Contract violations at each node boundary
  - Partial node failures mid-pipeline
  - HITL queue edge cases (overflow, duplicate IDs)
  - Pipeline with valid flow (smoke test)
"""

import copy
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from ontology_engine.pipeline import (
    ContractViolationError,
    PipelineError,
    _validate_contract,
)
from ontology_engine.contracts.validators import ContractViolation, validate_contract
from ontology_engine.hitl.review_queue import ReviewQueue


# ── K6.1: Contract Validation at Pipeline Level ────────────────────────────

class TestPipelineContractValidation:
    """Pipeline-level contract enforcement."""

    def test_invalid_node1_output_halts_pipeline(self):
        """Invalid Node 1 output should halt with ContractViolationError."""
        from ontology_engine.contracts.schemas import NODE_1_TO_2_SCHEMA
        invalid_data = {"text": "", "method": "native"}  # Missing required fields
        with pytest.raises(ContractViolationError):
            _validate_contract(invalid_data, NODE_1_TO_2_SCHEMA, "node1", "node2")

    def test_invalid_node2_output_halts_pipeline(self):
        """Invalid Node 2 output should halt with ContractViolationError."""
        from ontology_engine.contracts.schemas import NODE_2_TO_3_SCHEMA
        invalid_data = {"header": {}}  # Missing line_items, totals
        with pytest.raises(ContractViolationError):
            _validate_contract(invalid_data, NODE_2_TO_3_SCHEMA, "node2", "node3")

    def test_invalid_node3_output_halts_pipeline(self):
        """Invalid Node 3 output should halt with ContractViolationError."""
        from ontology_engine.contracts.schemas import NODE_3_TO_4_SCHEMA
        invalid_data = {"header": {}}  # Missing procurement_items, adjusted_totals
        with pytest.raises(ContractViolationError):
            _validate_contract(invalid_data, NODE_3_TO_4_SCHEMA, "node3", "node4")

    def test_valid_data_passes_pipeline_contract(self):
        """Valid data should pass pipeline contract validation."""
        from ontology_engine.contracts.schemas import NODE_1_TO_2_SCHEMA
        valid_data = {
            "text": "Valid text content",
            "method": "native",
            "confidence": 1.0,
            "page_count": 1,
            "pii_redacted": True,
        }
        # Should not raise
        _validate_contract(valid_data, NODE_1_TO_2_SCHEMA, "node1", "node2")


# ── K6.2: HITL Queue Stress Tests ──────────────────────────────────────────

class TestHITLQueueStress:
    """HITL review queue under stress conditions."""

    @pytest.fixture
    def queue(self, tmp_dir):
        """Create a ReviewQueue with a temp directory."""
        return ReviewQueue(queue_dir=tmp_dir / "hitl")

    def test_add_many_items(self, queue):
        """Adding many items should not degrade or crash."""
        for i in range(100):
            result = queue.add(
                [{"item": f"test_{i}", "description": f"Item {i}"}],
                reason="low_confidence",
                source_file=f"test_{i}.pdf",
            )
            assert result["queue_id"]
            assert result["status"] == "pending"

        pending = queue.list_pending()
        assert len(pending) == 100

    def test_approve_nonexistent_item(self, queue):
        """Approving a non-existent ID should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            queue.approve("00000000-0000-0000-0000-000000000000")

    def test_reject_nonexistent_item(self, queue):
        """Rejecting a non-existent ID should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            queue.reject("00000000-0000-0000-0000-000000000000")

    def test_double_approve(self, queue):
        """Approving an already-approved item should raise ValueError."""
        result = queue.add([{"item": "test"}], reason="f9_override")
        queue.approve(result["queue_id"])
        with pytest.raises(ValueError, match="pending"):
            queue.approve(result["queue_id"])

    def test_approve_then_reject(self, queue):
        """Rejecting an approved item should raise ValueError."""
        result = queue.add([{"item": "test"}], reason="f9_override")
        queue.approve(result["queue_id"])
        with pytest.raises(ValueError, match="pending"):
            queue.reject(result["queue_id"])

    def test_reject_then_approve(self, queue):
        """Approving a rejected item should raise ValueError."""
        result = queue.add([{"item": "test"}], reason="f9_override")
        queue.reject(result["queue_id"], reviewer_notes="Bad data")
        with pytest.raises(ValueError, match="pending"):
            queue.approve(result["queue_id"])

    def test_empty_queue_list_pending(self, queue):
        """Empty queue should return empty list, not error."""
        pending = queue.list_pending()
        assert pending == []

    def test_get_nonexistent(self, queue):
        """Getting a non-existent entry should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            queue.get("nonexistent-uuid")

    def test_add_empty_items_list(self, queue):
        """Adding empty items list should still create a valid entry."""
        result = queue.add([], reason="low_confidence")
        assert result["queue_id"]
        assert result["queued_items"] == []

    def test_corrupted_queue_file_skipped(self, queue, tmp_dir):
        """Corrupted JSON files in queue dir should be skipped gracefully."""
        # Add a valid item
        queue.add([{"item": "valid"}], reason="f9_override")

        # Inject a corrupted file
        corrupt_path = (tmp_dir / "hitl") / "corrupted.json"
        corrupt_path.write_text("NOT VALID JSON {{{{", encoding="utf-8")

        # list_pending should still work, skipping the corrupt file
        pending = queue.list_pending()
        assert len(pending) >= 1

    def test_very_large_single_entry(self, queue):
        """Single entry with many items should not crash."""
        large_items = [
            {"item": f"item_{i}", "description": f"Description {i}" * 50}
            for i in range(500)
        ]
        result = queue.add(large_items, reason="low_confidence")
        assert len(result["queued_items"]) == 500

        # Should be retrievable
        entry = queue.get(result["queue_id"])
        assert len(entry["queued_items"]) == 500


# ── K6.3: Pipeline Error Handling ──────────────────────────────────────────

class TestPipelineErrorHandling:
    """Pipeline should produce clear errors at each failure point."""

    def test_pipeline_error_is_exception(self):
        """PipelineError should be a proper Exception subclass."""
        err = PipelineError("test error")
        assert isinstance(err, Exception)
        assert str(err) == "test error"

    def test_contract_violation_error_attributes(self):
        """ContractViolationError should carry source/target node info."""
        err = ContractViolationError("node1", "node2", "bad data")
        assert err.source_node == "node1"
        assert err.target_node == "node2"
        assert "node1" in str(err)
        assert "node2" in str(err)

    def test_contract_violation_error_is_pipeline_error(self):
        """ContractViolationError should inherit from PipelineError."""
        err = ContractViolationError("node1", "node2", "test")
        assert isinstance(err, PipelineError)


# ── K6.4: Contract Validator Edge Cases ────────────────────────────────────

class TestContractValidatorEdgeCases:
    """Edge cases in the contract validation module."""

    def test_validate_returns_true_on_success(self):
        """Successful validation should return True explicitly."""
        result = validate_contract({
            "text": "Valid",
            "method": "native",
            "confidence": 1.0,
            "page_count": 1,
            "pii_redacted": True,
        }, "node1_to_2")
        assert result is True

    def test_validate_unknown_contract(self):
        """Unknown contract name should raise ValueError."""
        with pytest.raises(ValueError):
            validate_contract({}, "nonexistent_contract")

    def test_all_registered_contracts_exist(self):
        """All expected contracts should be registered."""
        from ontology_engine.contracts.validators import SCHEMAS
        expected = ["node1_to_2", "node2_to_3", "node3_to_4"]
        for name in expected:
            assert name in SCHEMAS, f"Missing contract: {name}"
