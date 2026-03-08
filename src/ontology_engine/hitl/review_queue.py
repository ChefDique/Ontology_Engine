"""
Review Queue — CONST_005

Local JSON-based queue for items requiring human approval before
proceeding to CRM injection.

Design by Contract:
  Invariant: NEVER auto-POST to CRM. Human must explicitly approve.
  Invariant: All queue state is persisted to disk as JSON for crash safety.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Default queue storage location
_DEFAULT_QUEUE_DIR = Path.home() / ".ontology_engine" / "hitl_queue"


class ReviewQueue:
    """Persistent JSON-based HITL review queue.

    Each queue entry is stored as an individual JSON file in the queue
    directory, enabling concurrent access and crash-safe persistence.

    Queue entry lifecycle:
        pending → approved | rejected
    """

    def __init__(self, queue_dir: Path | None = None):
        self.queue_dir = Path(queue_dir or _DEFAULT_QUEUE_DIR)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def add(self, items: list[dict], reason: str, source_file: str = "") -> dict:
        """Add items to the review queue.

        Args:
            items: List of flagged item dicts.
            reason: Why review is needed ('f9_override' | 'low_confidence' | 'credit_return').
            source_file: Original input file that produced these items.

        Returns:
            dict with keys:
                - queue_id: str (UUID)
                - queued_items: list
                - reason: str
                - status: 'pending'
                - created_at: ISO timestamp
        """
        queue_id = str(uuid.uuid4())
        entry = {
            "queue_id": queue_id,
            "status": "pending",
            "reason": reason,
            "source_file": source_file,
            "queued_items": items,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_at": None,
            "reviewer_notes": None,
        }

        # Persist to disk
        entry_path = self.queue_dir / f"{queue_id}.json"
        entry_path.write_text(json.dumps(entry, indent=2, default=str), encoding="utf-8")

        logger.info(
            "HITL queued: %s (%d items, reason=%s)",
            queue_id,
            len(items),
            reason,
        )

        return {
            "queue_id": queue_id,
            "queued_items": items,
            "reason": reason,
            "status": "pending",
            "created_at": entry["created_at"],
        }

    def list_pending(self) -> list[dict]:
        """List all pending review items.

        Returns:
            list of queue entry dicts with status='pending'.
        """
        pending = []
        for entry_path in sorted(self.queue_dir.glob("*.json")):
            try:
                entry = json.loads(entry_path.read_text(encoding="utf-8"))
                if entry.get("status") == "pending":
                    pending.append(entry)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to read queue entry %s: %s", entry_path.name, e)
        return pending

    def approve(self, queue_id: str, reviewer_notes: str = "") -> dict:
        """Approve a queued item for CRM injection.

        Args:
            queue_id: UUID of the queue entry.
            reviewer_notes: Optional notes from the human reviewer.

        Returns:
            Updated queue entry dict.

        Raises:
            FileNotFoundError: If queue_id does not exist.
            ValueError: If item is not in 'pending' status.
        """
        return self._update_status(queue_id, "approved", reviewer_notes)

    def reject(self, queue_id: str, reviewer_notes: str = "") -> dict:
        """Reject a queued item — it will NOT be sent to CRM.

        Args:
            queue_id: UUID of the queue entry.
            reviewer_notes: Reason for rejection.

        Returns:
            Updated queue entry dict.

        Raises:
            FileNotFoundError: If queue_id does not exist.
            ValueError: If item is not in 'pending' status.
        """
        return self._update_status(queue_id, "rejected", reviewer_notes)

    def get(self, queue_id: str) -> dict:
        """Get a specific queue entry by ID.

        Raises:
            FileNotFoundError: If queue_id does not exist.
        """
        entry_path = self.queue_dir / f"{queue_id}.json"
        if not entry_path.exists():
            raise FileNotFoundError(f"Queue entry not found: {queue_id}")
        return json.loads(entry_path.read_text(encoding="utf-8"))

    def _update_status(self, queue_id: str, new_status: str, notes: str) -> dict:
        """Update the status of a queue entry.

        Raises:
            FileNotFoundError: If queue_id does not exist.
            ValueError: If entry is not in 'pending' status.
        """
        entry_path = self.queue_dir / f"{queue_id}.json"
        if not entry_path.exists():
            raise FileNotFoundError(f"Queue entry not found: {queue_id}")

        entry = json.loads(entry_path.read_text(encoding="utf-8"))

        if entry["status"] != "pending":
            raise ValueError(
                f"Cannot {new_status} entry {queue_id}: "
                f"current status is '{entry['status']}', expected 'pending'"
            )

        entry["status"] = new_status
        entry["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        entry["reviewer_notes"] = notes

        entry_path.write_text(json.dumps(entry, indent=2, default=str), encoding="utf-8")

        logger.info(
            "HITL %s: %s (notes: %s)",
            new_status,
            queue_id,
            notes or "(none)",
        )

        return entry


# ── Module-level convenience function (backward-compatible) ─────────────

# Singleton instance for the default queue
_default_queue: ReviewQueue | None = None


def _get_default_queue() -> ReviewQueue:
    """Get or create the default singleton ReviewQueue."""
    global _default_queue
    if _default_queue is None:
        _default_queue = ReviewQueue()
    return _default_queue


def queue_for_review(items: list[dict], reason: str) -> dict:
    """Add items to the HITL review queue.

    Module-level convenience function that uses the default queue.

    Returns:
        dict with keys:
            - queued_items: list
            - queue_id: str
            - reason: str ('f9_override' | 'low_confidence' | 'credit_return')
    """
    return _get_default_queue().add(items, reason)
