"""Tests for the HITL review queue (TASK_F4).

Tests the ReviewQueue class lifecycle: add → list → approve/reject.
"""

import json
from pathlib import Path

import pytest

from ontology_engine.hitl.review_queue import ReviewQueue, queue_for_review


@pytest.fixture
def queue(tmp_path):
    """Create a ReviewQueue with a temporary directory."""
    return ReviewQueue(queue_dir=tmp_path / "queue")


@pytest.fixture
def sample_items():
    """Sample flagged items for testing."""
    return [
        {
            "type": "low_confidence",
            "confidence": 0.5,
            "reason": "Below threshold",
        },
        {
            "type": "credit_return",
            "description": "Removed roofing item",
        },
    ]


# ── Add Tests ─────────────────────────────────────────────────────────────

class TestQueueAdd:
    """Tests for adding items to the review queue."""

    def test_add_creates_entry(self, queue, sample_items):
        """Adding items creates a queue entry."""
        result = queue.add(sample_items, reason="low_confidence")
        assert result["queue_id"]
        assert result["status"] == "pending"
        assert result["reason"] == "low_confidence"
        assert len(result["queued_items"]) == 2

    def test_add_persists_to_disk(self, queue, sample_items):
        """Queue entry is persisted to a JSON file."""
        result = queue.add(sample_items, reason="test")
        entry_path = queue.queue_dir / f"{result['queue_id']}.json"
        assert entry_path.exists()

        stored = json.loads(entry_path.read_text())
        assert stored["queue_id"] == result["queue_id"]
        assert stored["status"] == "pending"

    def test_add_unique_ids(self, queue, sample_items):
        """Each queue entry gets a unique ID."""
        r1 = queue.add(sample_items, reason="test")
        r2 = queue.add(sample_items, reason="test")
        assert r1["queue_id"] != r2["queue_id"]

    def test_add_with_source_file(self, queue, sample_items):
        """Source file info is stored."""
        result = queue.add(sample_items, reason="test", source_file="/tmp/test.pdf")
        entry = queue.get(result["queue_id"])
        assert entry["source_file"] == "/tmp/test.pdf"


# ── List Tests ────────────────────────────────────────────────────────────

class TestQueueList:
    """Tests for listing pending queue items."""

    def test_list_empty(self, queue):
        """Empty queue returns empty list."""
        assert queue.list_pending() == []

    def test_list_shows_pending(self, queue, sample_items):
        """List returns only pending items."""
        queue.add(sample_items, reason="test1")
        queue.add(sample_items, reason="test2")
        pending = queue.list_pending()
        assert len(pending) == 2

    def test_list_excludes_approved(self, queue, sample_items):
        """Approved items are excluded from pending list."""
        r1 = queue.add(sample_items, reason="test1")
        queue.add(sample_items, reason="test2")
        queue.approve(r1["queue_id"])
        pending = queue.list_pending()
        assert len(pending) == 1


# ── Approve/Reject Tests ─────────────────────────────────────────────────

class TestQueueApproveReject:
    """Tests for approve/reject lifecycle."""

    def test_approve_updates_status(self, queue, sample_items):
        """Approving sets status to 'approved'."""
        result = queue.add(sample_items, reason="test")
        approved = queue.approve(result["queue_id"], reviewer_notes="Looks good")
        assert approved["status"] == "approved"
        assert approved["reviewer_notes"] == "Looks good"
        assert approved["reviewed_at"] is not None

    def test_reject_updates_status(self, queue, sample_items):
        """Rejecting sets status to 'rejected'."""
        result = queue.add(sample_items, reason="test")
        rejected = queue.reject(result["queue_id"], reviewer_notes="Bad data")
        assert rejected["status"] == "rejected"
        assert rejected["reviewer_notes"] == "Bad data"

    def test_approve_persists(self, queue, sample_items):
        """Approval is persisted to disk."""
        result = queue.add(sample_items, reason="test")
        queue.approve(result["queue_id"])
        entry = queue.get(result["queue_id"])
        assert entry["status"] == "approved"

    def test_cannot_approve_twice(self, queue, sample_items):
        """Cannot approve an already-approved item."""
        result = queue.add(sample_items, reason="test")
        queue.approve(result["queue_id"])
        with pytest.raises(ValueError, match="expected 'pending'"):
            queue.approve(result["queue_id"])

    def test_cannot_reject_approved(self, queue, sample_items):
        """Cannot reject an already-approved item."""
        result = queue.add(sample_items, reason="test")
        queue.approve(result["queue_id"])
        with pytest.raises(ValueError, match="expected 'pending'"):
            queue.reject(result["queue_id"])

    def test_approve_nonexistent_raises(self, queue):
        """Approving nonexistent entry raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            queue.approve("nonexistent-id")


# ── Get Tests ─────────────────────────────────────────────────────────────

class TestQueueGet:
    """Tests for retrieving queue entries."""

    def test_get_existing(self, queue, sample_items):
        """Can retrieve an existing entry."""
        result = queue.add(sample_items, reason="test")
        entry = queue.get(result["queue_id"])
        assert entry["queue_id"] == result["queue_id"]

    def test_get_nonexistent_raises(self, queue):
        """Getting nonexistent entry raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            queue.get("nonexistent-id")


# ── Convenience Function Tests ────────────────────────────────────────────

class TestQueueForReview:
    """Tests for the module-level queue_for_review function."""

    def test_queue_for_review_returns_dict(self, tmp_path, monkeypatch, sample_items):
        """queue_for_review returns expected dict structure."""
        # Redirect the default queue to a temp directory
        import ontology_engine.hitl.review_queue as rq
        monkeypatch.setattr(rq, "_default_queue", ReviewQueue(queue_dir=tmp_path / "q"))

        result = queue_for_review(sample_items, reason="f9_override")
        assert "queue_id" in result
        assert result["reason"] == "f9_override"
        assert result["status"] == "pending"
