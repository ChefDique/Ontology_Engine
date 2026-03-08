"""Human-in-the-Loop gate — approval queue for uncertain outputs.

Exports:
    ReviewQueue: Persistent JSON-based review queue class.
    queue_for_review: Module-level convenience function.
"""

from ontology_engine.hitl.review_queue import ReviewQueue, queue_for_review

__all__ = ["ReviewQueue", "queue_for_review"]
